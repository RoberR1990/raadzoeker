# Fase 3: één dossierbestand per domein, onderwerp en kruising (domein x gebied).
#   python src/dossier_data.py  -> docs/ontwerp/d/<slug>.json, d/index.json (zoeklijst, kruimelpad) en d/overzicht.json (startpagina, Domeinen)
# Bron: de domeinlabels (WERK/labels/domein.json, fase 1) en gebiedslabels (WERK/labels/gebied.json, fase 2).
# Zelfde velden als de onderwerpdossiers uit ontwerp_data.py, zodat dossier.html ze op dezelfde manier toont.
# Debatten: agendapunten van de gemeenteraad met dat domein (en bij een kruising: die het gebied noemen).
# Stadsbrede stukken (5 of meer gebieden genoemd) tellen niet mee bij een gebied.
import json,os,re,collections,statistics,datetime,glob,unicodedata
from paden import WERK,DOCS,STAND
import domeinen as D
from ontwerp_data import zload,iso,kort,motiekern

OUT=os.path.join(DOCS,'ontwerp','d')
def slug(s):   # gelijk aan slug() in ontwerp.js
    s=''.join(c for c in unicodedata.normalize('NFD',s.lower()) if unicodedata.category(c)!='Mn').replace('&',' ')
    return re.sub(r'[^a-z0-9]+','-',s).strip('-')
def dagen(a,b): return (datetime.date.fromisoformat(b)-datetime.date.fromisoformat(a)).days
def schrijf(naam,obj): json.dump(obj,open(os.path.join(OUT,naam),'w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))

def main():
    os.makedirs(OUT,exist_ok=True)
    LD=json.load(open(os.path.join(WERK,'labels','domein.json'),encoding='utf8'))
    LG=json.load(open(os.path.join(WERK,'labels','gebied.json'),encoding='utf8'))
    INFO=json.load(open(os.path.join(WERK,'labels','info.json'),encoding='utf8'))
    GB=json.load(open(os.path.join(WERK,'gebied','gebieden.json'),encoding='utf8'))['gebieden']
    ouder={r['id']:r['ouder'] for r in GB}; GNAAM={r['id']:r['naam'] for r in GB if r['niveau']=='gebied'}
    def gebieden(k):
        """gebieden (namen) die een stuk noemt of waar het bij hoort; leeg bij stadsbreed (>=5)"""
        gg={x[0] if x[0] in GNAAM else ouder.get(x[0]) for x in LG.get(k,[])}
        gg={GNAAM[g] for g in gg if g in GNAAM}
        return gg if len(gg)<5 else set()
    DN={s:n for s,n,_ in D.DOMEINEN}
    # stukken (iBabs) met hun sleutel in de labels
    ST=zload(os.path.join(DOCS,'data','ibabs','stukken.zst')); S=ST['soorten']
    sleutel={}
    for k,v in INFO.items():
        m=re.search(r'/Item/([0-9a-f-]{36})',v[4] or '')
        if m: sleutel[m.group(1)]=k
    STEM={}
    for key,bb in json.load(open(os.path.join(DOCS,'data','ibabs','moties.json'))).items():
        y,k=key.split(':'); STEM.setdefault(y,{})[int(k)]=bb
    for y,kk in list(STEM.items()):
        Y=zload(os.path.join(DOCS,'data','raad',f'{y}.zst'))
        for k,bb in kk.items(): m=Y['mo'][k]; STEM[bb]=[m[4],m[5],m[6],m[7],m[8]]
        del STEM[y]
    def rij(r):
        x=[r[1],r[2],r[3].split(' (')[0].split(' · ')[0],r[5],r[7] if r[7].startswith('http') else 'https://gemeenteraad.rotterdam.nl/Reports/Item/'+r[7],r[8]]
        if S[r[0]] in('Motie','Amendement','Initiatiefvoorstel'):
            c=motiekern(r[6])
            if r[8] in STEM: c['s']=STEM[r[8]]
            x.append(c)
        elif S[r[0]]=='Toezegging': x.append({'o':kort(re.sub(r'\s+',' ',r[6].split('\nStand van zaken')[0]),260)} if r[6] else {})
        else: x.append({})
        return x
    stuk=[]   # (rij, domein, gebieden)
    for r in ST['s']:
        k=sleutel.get(r[7]); d=LD.get(k,[None])[0] if k else None
        stuk.append((r,d,gebieden(k) if k else set()))
    # wijkraadstukken uit de tekstindex (signalen uit de wijken)
    WIJK=('Wijkraadadvies','Ongevraagd wijkraadadvies','Wijkraadstuk')
    wst=[(v,LD.get(k,[None])[0],gebieden(k)) for k,v in INFO.items() if k.startswith('t:') and v[0] in WIJK and LD.get(k,[None])[0]]
    wst.sort(key=lambda x:x[0][1],reverse=True)
    # debatten in de raad: per agendapunt woorden, sprekers en het langste fragment
    meta=json.load(open(os.path.join(DOCS,'data','raad','meta.json'),encoding='utf8')); SPK=meta['spk']; PAR=meta['par']
    AP={}; WY=collections.Counter(); WP=collections.Counter()
    for p in sorted(glob.glob(os.path.join(DOCS,'data','raad','*.zst'))):
        y=os.path.basename(p)[:4]; Y=zload(p); s=Y['s']
        for j,t in enumerate(s['t']):
            if s['k'][j] not in(0,4) or not t: continue
            nw=len(t.split()); WY[y]+=nw; pa=PAR[s['pa'][j]] if s['pa'][j]>=0 else None
            if pa: WP[pa]+=nw
            k=f'r:{y}:{s["i"][j]}'
            if not LD.get(k,[None])[0]: continue
            a=AP.get(k)
            if not a:
                M=Y['M'][s['m'][j]]; I=Y['I'][s['i'][j]]
                a=AP[k]=dict(d=M[0],a=M[1] or '',ti=(I[1]+' '+I[2]).strip()[:160],y=y,n=0,w=0,pw=collections.Counter(),sp=collections.Counter(),best=(0,'',0),dom=LD[k][0],geb=gebieden(k))
            a['n']+=1; a['w']+=nw
            if pa: a['pw'][pa]+=nw
            if s['sp'][j]>=0: a['sp'][SPK[s['sp'][j]][0]+(f' ({pa})' if pa else '')]+=nw
            if nw>a['best'][0] and nw<2000: a['best']=(nw,re.sub(r'\s+',' ',t[:340]).strip()+('…' if len(t)>340 else ''),s['k'][j])
    jaren=sorted(WY)
    alle_af=[]
    def afdatum(r): return iso((re.search(r'afgedaan ([\d-]+)',r[5]) or [None,''])[1])
    for r in ST['s']:
        if S[r[0]]=='Motie' and r[4]==5 and afdatum(r): alle_af.append(dagen(r[1],afdatum(r)))
    STAD_MED=round(statistics.median(alle_af))
    def laat(r): d=iso((re.search(r'verwacht ([\d-]+)',r[5]) or [None,''])[1]); return bool(d) and d<STAND

    def bouw(naam,groep,soort,pad,rs,aps,gebtel,ws):
        mot=[r for r in rs if S[r[0]]=='Motie']; aan=[r for r in mot if r[4] in(1,4,5)]; toez=[r for r in rs if S[r[0]]=='Toezegging']
        top=sorted(aps,key=lambda a:(-(a['d']>='2025'),-a['n']))[:6]
        tr=[round(100*sum(a['w'] for a in aps if a['y']==y)/max(1,WY[y]),1) for y in jaren]
        trn=[sum(1 for a in aps if a['y']==y) for y in jaren]
        pw=collections.Counter(); [pw.update(a['pw']) for a in aps]
        partijen=sorted([(p,round(100*c/WP[p],1)) for p,c in pw.items() if WP[p]>20000],key=lambda x:-x[1])
        pd=collections.Counter()
        for a in aps: pd[a['d']]+=a['n']
        dl=[dagen(r[1],afdatum(r)) for r in aan if r[4]==5 and afdatum(r)]
        ind=collections.Counter(r[3].split(' (')[0].strip() for r in mot if r[3]); ok=collections.Counter(r[3].split(' (')[0].strip() for r in aan if r[3])
        tz=collections.Counter(re.sub(r'\s*\(.*','',r[3].split(' · ')[0]).strip() for r in toez if r[3]); tzo=collections.Counter(re.sub(r'\s*\(.*','',r[3].split(' · ')[0]).strip() for r in toez if r[3] and r[4]==4)
        nip=[r for r in mot if r[8] in STEM and STEM[r[8]][1]>=0]
        nip.sort(key=lambda r:(abs(STEM[r[8]][1]-STEM[r[8]][2]),-int(r[1].replace('-',''))))
        tg=sum(gebtel.values()) or 1
        return {'naam':naam,'groep':groep,'soort':soort,'pad':pad,'termen':'','sub':[],'jaren':jaren,'trend':tr,'trendn':trn,'eenheid':'procent',
          'partijen':partijen,'college':[],'tsum':None,'ai':False,'stand':STAND,
          'moties':{'aangenomen':len(aan),'open':sum(1 for r in mot if r[4]==4),'afgedaan':sum(1 for r in mot if r[4]==5),'verworpen':sum(1 for r in mot if r[4]==2),
                    'te_laat':sum(1 for r in mot if r[4]==4 and laat(r)),'lijst':[rij(r) for r in mot if r[4]==4][:15],'af':[rij(r) for r in mot if r[4]==5][:12]},
          'toez':{'open':sum(1 for r in toez if r[4]==4),'te_laat':sum(1 for r in toez if r[4]==4 and laat(r)),'afgedaan':sum(1 for r in toez if r[4]==5),
                  'lijst':[rij(r) for r in toez if r[4]==4][:15],'af':[rij(r) for r in toez if r[4]==5][:12]},
          'sv':{'n':sum(1 for r in rs if S[r[0]]=='Schriftelijke vragen'),'lijst':[rij(r) for r in rs if S[r[0]]=='Schriftelijke vragen'][:6]},
          'rekenkamer':{'n':sum(1 for r in rs if S[r[0]]=='Rekenkamerrapport'),'lijst':[rij(r) for r in rs if S[r[0]]=='Rekenkamerrapport'][:5]},
          'brieven':[rij(r) for r in rs if S[r[0]] in('Collegebrief','Raadsvoorstel')][:8],
          'debatten':[[a['d'],a['a'],a['ti'],a['n'],a['best'][1],-1,0,[n for n,_ in a['sp'].most_common(3)],a['best'][2]] for a in top],
          'wijkstukken':[[v[1],v[2],v[0],v[4]] for v,_,_ in ws[:10]],
          'verdieping':{'tl':{'deb':sorted([d_,c] for d_,c in pd.items() if c>=2),'mot':[[r[1],{1:'a',4:'a',5:'a',2:'v',3:'i'}.get(r[4],'o')] for r in mot],
                              'toez':[r[1] for r in toez],'rk':[[r[1],r[2]] for r in rs if S[r[0]]=='Rekenkamerrapport']},
                        'pj':{y:[sum(1 for r in aan if r[1][:4]==y),sum(1 for r in aan if r[1][:4]==y and r[4]==5)] for y in jaren},
                        'dl':round(statistics.median(dl)) if dl else None,'dln':len(dl),'stad_dl':STAD_MED,
                        'ind':[[p,c,ok[p]] for p,c in ind.most_common(8)],'tz':[[w,c,tzo[w]] for w,c in tz.most_common(5)],
                        'nip':[rij(r) for r in nip[:6]],'ver':[],'wijk':{g:round(100*c/tg,1) for g,c in gebtel.items()}}}

    index=[]; overzicht={'stand':STAND,'gebieden':sorted(GNAAM.values()),'domeinen':[]}
    aps_all=list(AP.values())
    for ds,dn,_ in D.DOMEINEN:
        rs=[r for r,d,_ in stuk if d==ds]; aps=[a for a in aps_all if a['dom']==ds]
        gebtel=collections.Counter()
        for r,d,gg in stuk:
            if d==ds: gebtel.update(gg)
        for a in aps: gebtel.update(a['geb'])
        ws=[x for x in wst if x[1]==ds]
        sl=slug(dn); obj=bouw(dn,'Domeinen','domein',[['Domeinen','domeinen.html']],rs,aps,gebtel,ws)
        obj['gebieden']=dict(gebtel); obj['domein']=sl; schrijf(sl+'.json',obj)
        index.append({'slug':sl,'naam':dn,'groep':'Domein','soort':'domein','domein':sl})
        kr={}
        for gn in GNAAM.values():
            rg=[r for r,d,gg in stuk if d==ds and gn in gg]; ag=[a for a in aps if gn in a['geb']]; wg=[x for x in ws if gn in x[2]]
            n=len(rg)+len(ag)+len(wg); kr[gn]=n
            if n<5: continue
            ks=sl+'--'+slug(gn)
            o=bouw(f'{dn} in {gn}',dn,'kruising',[['Domeinen','domeinen.html'],[dn,'#'+sl]],rg,ag,{gn:1},wg); o['gebied']=gn; o['domein']=sl
            schrijf(ks+'.json',o); index.append({'slug':ks,'naam':f'{dn} in {gn}','groep':dn,'soort':'kruising','domein':sl,'gebied':gn})
        m=obj['moties']; t=obj['toez']
        overzicht['domeinen'].append({'slug':sl,'naam':dn,'open_moties':m['open'],'open_toez':t['open'],'te_laat':m['te_laat']+t['te_laat'],
            'nieuw':sum(1 for r in rs if r[1]>=STAND[:4]+'-07-01'),'stukken':len(rs),'debatten':len(aps),'kruising':kr})
        print(dn,len(rs),'stukken',len(aps),'debatten')
    # gebieden (14): alles wat het gebied noemt of eruit komt, voor de briefing van een gebied
    for gn in GNAAM.values():
        rg=[r for r,d,gg in stuk if gn in gg]; ag=[a for a in aps_all if gn in a['geb']]; wg=[x for x in wst if gn in x[2]]
        o=bouw(gn,'Gebieden','gebied',[['Gebieden','wijk.html']],rg,ag,{gn:1},wg); o['gebied']=gn
        o['ai']=os.path.exists(os.path.join(DOCS,'ontwerp','samenvattingen',slug(gn)+'.json'))   # AI-samenvatting (gebied_in.py)
        schrijf(slug(gn)+'.json',o); index.append({'slug':slug(gn),'naam':gn,'groep':'Gebied','soort':'gebied','gebied':gn,'ai':o['ai']})
    # onderwerpen (38) en het overkoepelende onderwerp Parkeren: bestaande dossiers, nu onder een domein
    TH={'Parkeren':'mobiliteit','Mobiliteit & verkeer':'mobiliteit','Buitenruimte & afval':'buitenruimte','Veiligheid & handhaving':'veiligheid','Economie & haven':'economie',
        'Cultuur, sport & evenementen':'cultuur','Werk & inkomen':'werk','Wonen':'wonen','Zorg, welzijn & jeugd':'zorg','Asiel & migratie':'samenleven','Energie & klimaat':'klimaat',
        'Onderwijs':'onderwijs','Bouwen & ruimte':'wonen','Financiën & belastingen':'financien','Dienstverlening & organisatie':'bestuur','Discriminatie & inclusie':'samenleven','Participatie & inspraak':'bestuur'}
    ond=json.load(open(os.path.join(DOCS,'ontwerp','onderwerpen.json'),encoding='utf8'))['onderwerpen']
    dos=json.load(open(os.path.join(DOCS,'ontwerp','dossiers.json'),encoding='utf8'))['dossiers']
    pk=next(x for x in dos if x['naam']=='Parkeren')
    pk=dict(pk,soort='onderwerp',groep=DN['mobiliteit'],pad=[['Domeinen','domeinen.html'],[DN['mobiliteit'],'#'+slug(DN['mobiliteit'])]],stand=STAND)
    pk['ai']=os.path.exists(os.path.join(DOCS,'ontwerp','samenvattingen','parkeren.json'))
    schrijf('parkeren.json',pk); index.append({'slug':'parkeren','naam':'Parkeren','groep':DN['mobiliteit'],'soort':'onderwerp','domein':slug(DN['mobiliteit']),'sub':pk['sub'],'termen':pk['termen'],'ai':pk['ai']})
    for o in ond:
        ds=TH.get(o['groep']);
        if not ds: print('geen domein voor',o['naam'],o['groep']); continue
        pad=[['Domeinen','domeinen.html'],[DN[ds],'#'+slug(DN[ds])]]+([['Parkeren','#parkeren']] if o['groep']=='Parkeren' else [])
        sl=slug(o['naam']); x=dict(o,groep='Parkeren' if o['groep']=='Parkeren' else DN[ds],pad=pad,stand=STAND,ai=os.path.exists(os.path.join(DOCS,'ontwerp','samenvattingen',sl+'.json')))
        schrijf(sl+'.json',x); index.append({'slug':sl,'naam':o['naam'],'groep':x['groep'],'soort':'onderwerp','domein':slug(DN[ds]),'ai':x['ai'],'sub':[],'termen':o['termen']})
    schrijf('index.json',{'stand':STAND,'d':index}); schrijf('overzicht.json',overzicht)
    # filters voor Zoeken: per document in de tekstindex het domein en de gebieden (bitmasker)
    import zstandard
    meta=zload(os.path.join(DOCS,'data','tekst','meta.zst')); SL=[x[0] for x in D.DOMEINEN]; GL=sorted(GNAAM.values())
    dd=[];gm=[]
    for i in range(len(meta['d'])):
        k=f't:{i}'; d=LD.get(k,[None])[0]; dd.append(SL.index(d) if d in SL else -1)
        gm.append(sum(1<<GL.index(g) for g in gebieden(k)))
    raw=json.dumps({'dom':[[slug(DN[x]),DN[x]] for x in SL],'geb':GL,'d':dd,'g':gm},separators=(',',':')).encode()
    open(os.path.join(DOCS,'data','tekst','labels.zst'),'wb').write(zstandard.ZstdCompressor(level=19).compress(raw))
    # stand in de pagina's
    js=os.path.join(DOCS,'ontwerp','ontwerp.js'); t=open(js,encoding='utf8').read()
    open(js,'w',encoding='utf8').write(re.sub(r"const STAND='[\d-]+';",f"const STAND='{STAND}';",t))
    print(len(index),'dossiers;',sum(os.path.getsize(os.path.join(OUT,f)) for f in os.listdir(OUT))//1000,'kB totaal')

if __name__=='__main__': main()
