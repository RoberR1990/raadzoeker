# Invoerpakket voor een holistische AI-samenvatting van één onderwerp (onderwerpen.py), nadruk 2022+.
#   python src/dossier_in.py <nr>   (nr = positie in onderwerpen.O, vanaf 1)  -> WERK/dossier/in_<slug>.md en bronnen_<slug>.json
# Elke bron krijgt een code (D = debat, M = motie/amendement, T = toezegging, V = schriftelijke vragen, S = overig stuk,
# W = wijkraad). De samenvatting moet per bewering een code + letterlijk citaat geven; dossier_check.py controleert dat.
import json,os,re,sys,glob,collections,zstandard
import teksten as T
from onderwerpen import O,rx
from paden import WERK,DOCS
DZ=zstandard.ZstdDecompressor()
def zload(p): return json.loads(DZ.decompress(open(p,'rb').read(),max_output_size=10**9))
def slug(s): return re.sub(r'[^a-z0-9]+','-',T.fold(s)).strip('-')
def ws(s): return re.sub(r'\s+',' ',s).strip()
def vensters(t,r,n=4,breed=700,kop=400):
    """Begin van het stuk plus vensters rond de treffers (niet overlappend)."""
    f=T.fold(t); uit=[]; bezet=[]
    if kop: uit.append((0,min(len(t),kop))); bezet.append((0,kop))
    for m in r.finditer(f):
        a=max(0,m.start()-breed//2); b=min(len(t),a+breed)
        if any(a<y and b>x for x,y in bezet): continue
        uit.append((a,b)); bezet.append((a,b))
        if len(uit)>n: break
    uit.sort()
    return ' […] '.join(('…' if a else '')+ws(t[a:b])+('…' if b<len(t) else '') for a,b in uit)
def main(nr):
    naam,pp=O[nr-1]; pakket(naam,rx(pp))
def pakket(naam,r,kopnaam='het onderwerp',extra=None):
    """Bronnenpakket voor een onderwerp of gebied: r = regex op gevouwen tekst."""
    s=slug(naam)
    B={}; L=[]
    # debatten raad + commissies
    deb=[]
    for bron in('raad','commissies'):
        meta=json.load(open(f'{DOCS}/data/{bron}/meta.json',encoding='utf8')); SPK=meta['spk']; PAR=meta['par']; ROL=meta.get('roles',[])
        for p in sorted(glob.glob(f'{DOCS}/data/{bron}/20*.zst')):
            Y=zload(p); S=Y['s']
            for i,t in enumerate(S['t']):
                if S['k'][i] not in(0,4) or not t: continue
                h=r.findall(T.fold(t))
                if not h: continue
                M=Y['M'][S['m'][i]]; I=Y['I'][S['i'][i]]
                wie=SPK[S['sp'][i]][0] if S['sp'][i]>=0 else 'onbekend'
                rol=ROL[S['ro'][i]] if S['ro'][i]>=0 and S['ro'][i]<len(ROL) else ''
                deb.append({'datum':M[0],'verg':('Gemeenteraad' if bron=='raad' else M[2]),'punt':ws(I[2])[:160],'wie':wie,'partij':PAR[S['pa'][i]] if S['pa'][i]>=0 else '',
                            'rol':rol if isinstance(rol,str) else str(rol),'auto':S['k'][i]==4,'n':len(h),'tekst':t,
                            'url':('https://gemeenteraad.rotterdam.nl/Agenda/Index/'+M[1]) if M[1] else ''})
    recent=sorted([d for d in deb if d['datum']>='2022'],key=lambda d:(-d['n'],d['datum']))[:140]
    oud=sorted([d for d in deb if d['datum']<'2022'],key=lambda d:-d['n'])[:20]
    for k,d in enumerate(sorted(recent+oud,key=lambda d:d['datum']),1):
        c=f'D{k}'; d['tekst']=vensters(d['tekst'],r,n=2,breed=900,kop=0) if len(d['tekst'])>1400 else ws(d['tekst'])
        B[c]={x:d[x] for x in('datum','verg','punt','wie','partij','rol','auto','url','tekst')}
    # moties, amendementen, toezeggingen met status (stukken.zst) en stemuitslag uit de notulen
    ST=zload(f'{DOCS}/data/ibabs/stukken.zst'); SO=ST['soorten']
    km=kt=0
    for row in sorted(ST['s'],key=lambda x:x[1]):
        so=SO[row[0]]
        if so not in('Motie','Amendement','Toezegging'): continue
        f=T.fold(row[2]+' '+row[6])
        if not (r.search(T.fold(row[2])) or len(r.findall(f))>=2): continue
        if row[1]<'2022' and so=='Toezegging': continue
        url=row[7] if row[7].startswith('http') else 'https://gemeenteraad.rotterdam.nl/Reports/Item/'+row[7]
        if so=='Toezegging': kt+=1; c=f'T{kt}'
        else: km+=1; c=f'M{km}'
        B[c]={'soort':so,'datum':row[1],'titel':row[2],'wie':row[3],'status':row[5],'url':url,'tekst':vensters(row[6],r,n=3,breed=600,kop=900)}
    # overige stukken met volledige tekst
    kv=ks=kw=0
    for key,so,datum,titel,wie,url,t in T.bronnen():
        if key.startswith('st:') and so in('Motie','Amendement','Toezegging'): continue
        if (datum or '')<'2022' and so!='Rekenkamerrapport': continue
        f=T.fold((titel or '')+' '+t)
        if not (r.search(T.fold(titel or '')) or len(r.findall(f))>=(2 if so=='Schriftelijke vragen' else 3)): continue   # lange stukken: minstens 3 treffers
        if so=='Schriftelijke vragen':
            kv+=1; c=f'V{kv}'; v,_,a=t.partition('\n\nANTWOORD VAN HET COLLEGE')
            tekst='VRAGEN: '+vensters(v,r,n=2,breed=700,kop=1200)+('\nANTWOORD VAN HET COLLEGE'+vensters(a,r,n=3,breed=800,kop=600) if a else '\n(geen antwoord gevonden)')
        elif so.startswith(('Wijk','Ongevraagd','Collegereactie')):
            kw+=1; c=f'W{kw}'; tekst=vensters(t,r,n=2,breed=600,kop=300)
        else:
            ks+=1; c=f'S{ks}'; tekst=vensters(t,r,n=3,breed=700,kop=500)
        B[c]={'soort':so,'datum':datum,'titel':ws(titel or ''),'wie':ws(wie or ''),'url':url,'tekst':tekst}
    # te veel wijkraadstukken: de meest relevante 80
    for g,mx in(('W',60),('S',50),('V',140),('M',130),('T',120),('D',120)):   # te veel stukken: de meest relevante houden
        W=[c for c in B if c[0]==g]
        if len(W)>mx:
            keep=set(sorted(W,key=lambda c:-len(r.findall(T.fold(B[c].get('titel',B[c].get('punt',''))*2+' '+B[c]['tekst']))))[:mx])
            for c in W:
                if c not in keep: del B[c]
    if extra: B.update(extra)   # bijv. het coalitieakkoord als stuk (S-code)
    os.makedirs(os.path.join(WERK,'dossier'),exist_ok=True)
    json.dump({'onderwerp':naam,'bronnen':B},open(os.path.join(WERK,'dossier',f'bronnen_{s}.json'),'w',encoding='utf8'),ensure_ascii=False)
    # leesbare invoer voor het model
    kop={'D':'DEBATTEN (raad en commissies; "auto" = automatische ondertiteling, kan fouten bevatten)','M':'MOTIES EN AMENDEMENTEN','T':'TOEZEGGINGEN VAN HET COLLEGE',
         'V':'SCHRIFTELIJKE VRAGEN VAN RAADSLEDEN MET ANTWOORD VAN HET COLLEGE','S':'RAADSVOORSTELLEN, COLLEGEBRIEVEN, REKENKAMER EN OVERIGE STUKKEN','W':'WIJKRADEN'}
    out=[f'# Bronnen voor {kopnaam}: {naam}','']
    for g in 'DMTVSW':
        cs=[c for c in B if c[0]==g]
        if not cs: continue
        out+=[f'## {kop[g]} ({len(cs)})','']
        for c in cs:
            b=B[c]
            if g=='D': hd=f"[{c}] {b['datum']} · {b['verg']} · {b['punt']} · {b['wie']}{' ('+b['partij']+')' if b['partij'] else ''}{' · auto' if b['auto'] else ''}"
            else: hd=f"[{c}] {b['datum']} · {b['soort']} · {b['titel']}{' · '+b['wie'] if b['wie'] else ''}{' · status: '+b['status'] if b.get('status') else ''}"
            out+=[hd,b['tekst'],'']
    p=os.path.join(WERK,'dossier',f'in_{s}.md'); open(p,'w',encoding='utf8').write('\n'.join(out))
    n=collections.Counter(c[0] for c in B)
    print(naam,dict(n),round(os.path.getsize(p)/1000),'kB',p)
if __name__=='__main__': main(int(sys.argv[1]))
