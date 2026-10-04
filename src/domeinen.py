# Fase 1: domeinen (taxonomie) en domeinlabels voor alle stukken en agendapunten.
#   python src/domeinen.py            -> WERK/labels/domein.json + rapport in WERK/labels/domein_rapport.txt
# Methode per label, in volgorde van zekerheid:
#   bron      beleidsveld dat iBabs zelf aan het stuk geeft (zekerheid 1)
#   regel     procedureel agendapunt of stuk (opening, besluitenlijst, ...) -> geen domein
#   woordmodel  naive Bayes op titel + begin van de tekst, getraind op de bronlabels; zekerheid = kans van het model.
#             Bij commissievergaderingen alleen de domeinen van die commissie (afgeleid uit de bronlabels).
import json,os,re,glob,collections,random,zstandard,math
import numpy as np
import teksten as T
from paden import WERK,DOCS

# slug, naam, iBabs-beleidsvelden
DOMEINEN=[
 ('wonen','Wonen en bouwen',['Bouwen en Wonen','Wonen','Bouwen','Vastgoed','Projecten']),
 ('buitenruimte','Buitenruimte',['Buitenruimte']),
 ('mobiliteit','Mobiliteit',['Mobiliteit']),
 ('economie','Economie en haven',['Economie','Haven','Horeca']),
 ('klimaat','Klimaat en energie',['Duurzaam','Duurzaamheid']),
 ('veiligheid','Veiligheid',['Veiligheid']),
 ('zorg','Zorg, welzijn en jeugd',['Zorg','Welzijn','Volksgezondheid','Jeugd','Jeugd (2010-2014)']),
 ('onderwijs','Onderwijs',['Onderwijs','Onderwijs en Jeugd','Onderwijs (2010-2014)']),
 ('werk','Werk, inkomen en armoede',['Werk en Inkomen','Armoedebestrijding','Schulddienstverlening','Armoede en schulden','NPRZ']),
 ('samenleven','Samenleven en participatie',['Samenleven','Integratie','Participatie']),
 ('cultuur','Cultuur en sport',['Cultuur','Sport','Sport en recreatie']),
 ('bestuur','Bestuur en organisatie',['Bestuur','Organisatie','Wijken','Gebieden','Bestuur (2010-2014)','PRESIDIUM','Algemeen']),
 ('financien','Financiën',['Financiën','Financïen','Financien-inactief','Financiële verantwoording','cor']),
]
BV={b:s for s,_,bb in DOMEINEN for b in bb}
NAAM={s:n for s,n,_ in DOMEINEN}
SL=[s for s,_,_ in DOMEINEN]

# procedurele titels: geen domein
PROC=re.compile(r'^\W*(opening|sluiting|vaststell\w* (van )?(de )?(agenda|notulen|besluitenlijst|verslag)|vaststellen (agenda|notulen)|mededelingen|ingekomen stukken|'
  r'rondvraag|notulen|besluitenlijst|presentielijst|agenda\b|actualiteiten gemeenteraad|vragenuur|beëdiging|installatie|toelating|benoeming|'
  r'stemverklaring|schorsing|heropening|lijst (met|van) (ingekomen|toezeggingen|openstaande)|termijnagenda|voorzittersverkiezing|procedurevergadering|'
  r'verslag (van )?de (vorige )?vergadering|uitnodiging|nieuwsbrief|wijkraad \w+.*(formeel|informeel)|adviezenlijst|commissieplanning|lange.termijn.?agenda|'
  r'uitzending|hamerstukken|regeling van (de )?werkzaamheden|mededeling (van )?(de )?ingekomen|agendabundel|actielijst|actiepunten|onderzoek (van de )?geloofsbrieven|initiatiefnotities/voorstellen|lijsten? (met|van) openstaande|tweeminutendebatten|interpellatiedebatten|$)|besluitenlijst|^\W*(agp|agendapunt)\.? ?\w*\W+(notulen|agenda|verslag)',re.I)

def jl(p):
    if os.path.exists(p):
        for l in open(p,encoding='utf8'):
            try: yield json.loads(l)
            except ValueError: pass

MAAND={m:k+1 for k,m in enumerate('januari februari maart april mei juni juli augustus september oktober november december'.split())}
def ibabs_velden():
    """item-id -> (beleidsvelden, commissie); bb-nummer -> beleidsvelden; (datum, nr, vergadering) -> Counter(domein) via het veld Agendapunt."""
    out={}; bbd={}; apd=collections.defaultdict(collections.Counter)
    for p in glob.glob(os.path.join(WERK,'ibabs','items_*.jsonl'))+[os.path.join(WERK,'ibabs','sv_qa.jsonl')]:
        for r in jl(p):
            d=r.get('detail') or {}; L=r.get('lijst') or {}
            b=d.get('Beleidsveld') or L.get('beleidsveld') or ''
            bb=[x.strip() for x in re.split(r'[\n|,]',str(b)) if x.strip()]
            out[r['id']]=(bb,(d.get('Commissie') or L.get('commissie') or '').strip())
            dd=[BV[x] for x in bb if x in BV]
            nr=d.get('BB-nummer') or d.get('BB nummer') or L.get('externalid')
            if nr and dd: bbd[nr]=dd
            a=d.get('Agendapunt')
            m=re.match(r'\s*(.+?)\s+(\d{4})\s*\n\s*\(([\d.]+?)\.?\s.*?\n\s*\w+dag (\d+) (\w+)',a or '',re.S)
            if m and dd and m.group(5) in MAAND:
                verg='raad' if m.group(1).startswith('Gemeenteraad') else normcom(m.group(1))
                apd[(f'{m.group(2)}-{MAAND[m.group(5)]:02d}-{int(m.group(4)):02d}',m.group(3).rstrip('.'),verg)][dd[0]]+=1
    return out,bbd,apd

def tekstdocs():
    dz=zstandard.ZstdDecompressor(); D=os.path.join(DOCS,'data','tekst')
    m=json.loads(dz.decompress(open(os.path.join(D,'meta.zst'),'rb').read(),max_output_size=10**9))
    blok={}
    def tekst(i):
        b=i//m['blok']
        if b not in blok: blok[b]=json.loads(dz.decompress(open(os.path.join(D,'b',f'{b:03d}.zst'),'rb').read(),max_output_size=10**9))
        return blok[b][i%m['blok']]
    return m,tekst

def agendapunten():
    """[(sleutel, soort, datum, vergadering, titel, begin van de spreekbeurten)] voor raad en commissies."""
    dz=zstandard.ZstdDecompressor(); out=[]
    MO=json.load(open(os.path.join(DOCS,'data','ibabs','moties.json'),encoding='utf8'))
    for k,pre in (('raad','r'),('commissies','c')):
        for p in sorted(glob.glob(os.path.join(DOCS,'data',k,'*.zst'))):
            y=os.path.basename(p)[:4]; Y=json.loads(dz.decompress(open(p,'rb').read(),max_output_size=10**9))
            S=Y['s']; per=collections.defaultdict(list); mo=collections.defaultdict(list)
            for k2,m in enumerate(Y.get('mo',[])):
                if f'{y}:{k2}' in MO: mo[S['i'][m[0]]].append(MO[f'{y}:{k2}'])
            for j,i in enumerate(S['i']):
                if S['k'][j] in (0,4) and len(per[i])<60: per[i].append(S['t'][j])
            for i,(mi,nr,tit) in enumerate(Y['I']):
                if i not in per: continue
                M=Y['M'][mi]
                out.append((f'{pre}:{y}:{i}','Raadsdebat' if pre=='r' else 'Commissiedebat',M[0],M[2],tit,' '.join(per[i]),nr,mo[i]))
    return out

def woorden(titel,tekst,n=150):
    w=T.woorden(tekst)[:n]
    return T.woorden(titel)*3+w

class NB:
    def fit(self,X,y,alpha=0.1):
        voc=collections.Counter(w for x in X for w in set(x))
        self.v={w:k for k,(w,c) in enumerate(voc.most_common()) if c>=3}
        C=np.full((len(SL),len(self.v)),alpha); pri=np.zeros(len(SL))
        for x,c in zip(X,y):
            pri[c]+=1
            for w,n in collections.Counter(x).items():
                if w in self.v: C[c,self.v[w]]+=1+math.log(n)
        self.lp=np.log(C/C.sum(1,keepdims=True)); self.pri=np.log((pri+1)/(pri.sum()+len(SL)))
        return self
    def proba(self,x,toegestaan=None):
        idx=collections.Counter(self.v[w] for w in x if w in self.v)
        s=self.pri.copy()
        for k,n in idx.items(): s+=self.lp[:,k]*(1+math.log(n))
        if toegestaan is not None: s=np.where(toegestaan,s,-1e18)
        s-=s.max(); p=np.exp(s); return p/p.sum()

def main():
    random.seed(1)
    iv,bbd,apd=ibabs_velden(); m,tekst=tekstdocs(); S=m['soorten']
    items=[]   # (sleutel, soort, datum, titel, wie, woorden, bronlabel, commissie)
    for i,r in enumerate(m['d']):
        mm=re.search(r'/Item/([0-9a-f-]{36})',r[4] or ''); bb,com=iv.get(mm.group(1),([],'')) if mm else ([],'')
        dd=[BV[b] for b in bb if b in BV]
        items.append(dict(k=f't:{i}',soort=S[r[0]],datum=r[1],titel=r[2],wie=r[3],url=r[4],w=woorden(r[2],tekst(i)),bron=list(dict.fromkeys(dd)),com=com))
    # model trainen op de bronlabels (eerste beleidsveld), met 5-voudige kruisvalidatie
    L=[x for x in items if x['bron']]; random.shuffle(L)
    rep=[]; cv=[]
    for f in range(5):
        te=L[f::5]; tr=[x for k,x in enumerate(L) if k%5!=f]
        nb=NB().fit([x['w'] for x in tr],[SL.index(x['bron'][0]) for x in tr])
        for x in te:
            p=nb.proba(x['w']); k=int(p.argmax()); cv.append((float(p[k]),SL[k] in x['bron'],x['soort']))
    rep.append(f'Woordmodel, kruisvalidatie op {len(cv)} stukken met bronlabel: {sum(c for _,c,_ in cv)/len(cv):.1%} juist (een van de bron-beleidsvelden)')
    for lo in (0,.5,.7,.8,.9,.95,.99):
        s=[c for p,c,_ in cv if p>=lo]; rep.append(f'  zekerheid >= {lo:.2f}: {len(s)/len(cv):6.1%} van de stukken, {sum(s)/max(1,len(s)):.1%} juist')
    nb=NB().fit([x['w'] for x in L],[SL.index(x['bron'][0]) for x in L])
    # commissie -> domeinen (aandeel >= 8% van de stukken met bronlabel in die commissie)
    cx=collections.defaultdict(collections.Counter)
    for x in L:
        if x['com']: cx[normcom(x['com'])][x['bron'][0]]+=1
    COM={}
    rep.append('\nCommissie -> domeinen (aandeel stukken met dat beleidsveld):')
    for c,cnt in sorted(cx.items(),key=lambda kv:-sum(kv[1].values())):
        n=sum(cnt.values())
        if n<20: continue
        COM[c]=[d for d,v in cnt.items() if v/n>=.08]
        rep.append(f'  {c} ({n}): '+', '.join(f'{NAAM[d]} {v/n:.0%}' for d,v in cnt.most_common() if v/n>=.03))
    # labelen
    out={}; tel=collections.Counter()
    def zet(x,dom,meth,z,extra=None):
        out[x['k']]=[dom,meth,round(z,3)]+([extra] if extra else [])
        tel[(x['soort'],meth if dom else 'geen')]+=1
    for x in items:
        if x['bron']: zet(x,x['bron'][0],'bron',1.0,x['bron'][1] if len(x['bron'])>1 else None)
        elif x['soort'] in ('Wijkraadvergadering','Wijkverslag','Wijkakkoord of wijkplan','Collegereactie op wijkplan'): zet(x,None,'regel',1.0)   # vergadering of plan over alles
        elif PROC.search(x['titel']): zet(x,None,'regel',1.0)
        else:
            p=nb.proba(x['w']); k=int(p.argmax()); zet(x,SL[k],'woordmodel',float(p[k]))
    ap=agendapunten()
    for k,soort,datum,verg,tit,tx,nr,mos in ap:
        x=dict(k=k,soort=soort,titel=tit)
        if PROC.search(tit) or re.match(r'^\W*(actualiteitenraad|motie vreemd)',tit,re.I) and len(tit)<45: zet(x,None,'regel',1.0); continue
        c=normcom(verg)
        # kopje in de commissieagenda dat zelf een beleidsveld is (bijv. '1.04.02. Zorg')
        kop=re.sub(r'^[\d. ]+','',tit).strip().rstrip('.')
        if soort=='Commissiedebat' and kop in BV: zet(x,BV[kop],'bron',1.0); continue
        # gekoppelde iBabs-stukken: op hetzelfde agendapunt geagendeerd, of moties die bij dit punt zijn ingediend
        cnt=collections.Counter(apd.get((datum,nr,'raad' if soort=='Raadsdebat' else c),{}))
        for b in mos:
            for d in bbd.get(b,[])[:1]: cnt[d]+=1
        if cnt:
            d,n=cnt.most_common(1)[0]; tot=sum(cnt.values())
            if n/tot>=.5: zet(x,d,'gekoppeld',n/tot,(cnt.most_common(2)[1][0] if len(cnt)>1 else None)); continue
        ok=None
        if soort=='Commissiedebat' and c in COM: ok=np.array([s in COM[c] for s in SL])
        p=nb.proba(woorden(tit,tx,300),ok); j=int(p.argmax()); zet(x,SL[j],'woordmodel',float(p[j]))
    os.makedirs(os.path.join(WERK,'labels'),exist_ok=True)
    json.dump(out,open(os.path.join(WERK,'labels','domein.json'),'w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
    # meta voor steekproef en rapport
    info={x['k']:[x['soort'],x['datum'],x['titel'],x['wie'],x['url']] for x in items}
    info.update({a[0]:[a[1],a[2],a[4],a[3],''] for a in ap})
    json.dump(info,open(os.path.join(WERK,'labels','info.json'),'w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
    json.dump(COM,open(os.path.join(WERK,'labels','commissies.json'),'w',encoding='utf8'),ensure_ascii=False,indent=1)
    rep.append(f'\nGelabeld: {len(out)}  (stukken {len(items)}, agendapunten {len(ap)})')
    for (s,meth),n in sorted(tel.items()): rep.append(f'  {s:28} {meth:11} {n}')
    zz=collections.Counter();
    for k,v in out.items():
        if v[1]=='woordmodel': zz['>=0.9' if v[2]>=.9 else '0.7-0.9' if v[2]>=.7 else '<0.7']+=1
    rep.append(f'Woordmodel-zekerheid: {dict(zz)}')
    dc=collections.Counter(v[0] for v in out.values() if v[0])
    rep.append('Per domein: '+', '.join(f'{NAAM[d]} {n}' for d,n in dc.most_common()))
    open(os.path.join(WERK,'labels','domein_rapport.txt'),'w',encoding='utf8').write('\n'.join(rep))
    print('\n'.join(rep))

AFK={'BWB':'Bouwen, Wonen en Buitenruimte (2022-2026)','MHEK':'Mobiliteit, Haven, Economie en Klimaat (2022-2026)','BOFV':'Bestuur, Organisatie, Financiën en Veiligheid (2022-2026)',
     'ZWCS':'Zorg, Welzijn, Cultuur en Sport (2022-2026)','WIOSSAN':'Werk & Inkomen, Onderwijs, Samenleven, Schuldhulpverlening, Armoedebestrijding & NPRZ (2022-2026)',
     'EDEM':'Energietransitie, Duurzaamheid, Economie en Mobiliteit (2018-2022)','ZOCS':'Zorg, Onderwijs, Cultuur en Sport (2018-2022)','VB':'Veiligheid en Bestuur (2018-2022)',
     'WIISA':'Werkgelegenheid, Inkomen, Integratie, Schuldenaanpak en Armoedebestrijding (2018-2022)','MPOF':'Majeure Projecten, Organisatie en Financien (2018-2022)',
     'COR':'tot Onderzoek van de Rekening'}
def normcom(c):
    c=re.sub(r'^(Commissie|Subcommissie bestemmingsplannen Commissie)\s+','',(c or '').split('\n')[0].strip())
    c=AFK.get(c.upper(),c) if c.upper() in AFK else c
    c=c.replace('&','en').replace(' - ','-').replace(',',' ').replace('  ',' ')
    c=re.sub(r'\s+',' ',c).strip()
    if c.startswith('tot Onderzoek van de Rekening'): c='tot Onderzoek van de Rekening'
    return c

if __name__=='__main__': main()
