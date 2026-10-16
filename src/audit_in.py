# Inhoudelijke controle van gepubliceerde samenvattingen (docs/samenvattingen/*.json), aanvulling op dossier_check.py.
# dossier_check toetst alleen of het citaat woordelijk in de bron staat; deze controle legt elke zin naast het citaat
# én de omringende brontekst, zodat een model kan beoordelen of de zin er echt door gedekt wordt (niet te ruim,
# juiste spreker/fractie, juiste periode).
#   python src/audit_in.py in [slug ...]    -> WERK/audit/in_<slug>.md (genummerde punten met context)
#   python src/audit_in.py toepassen <slug> -> leest WERK/audit/oordeel_<slug>.json, schrapt/herschrijft in docs/samenvattingen/<slug>.json
# Oordeel (per nummer): ok | te_ruim (met 'nieuw': strakkere zin) | onjuist | toeschrijving (verkeerde spreker/fractie) -> laatste twee worden geschrapt.
import json,os,re,sys,glob,datetime,zstandard
import teksten as T
from paden import WERK,DOCS
DZ=zstandard.ZstdDecompressor()
def zload(p): return json.loads(DZ.decompress(open(p,'rb').read(),max_output_size=10**9))
SD=os.path.join(DOCS,'samenvattingen'); AD=os.path.join(WERK,'audit')
def ws(s): return re.sub(r'\s+',' ',s or '').strip()
def punten(S):
    """Alle te controleren punten: (pad, item, tekstveld, extra)."""
    for i,x in enumerate(S.get('kern') or []): yield ('kern',i),x,'zin',''
    for a,p in enumerate(S.get('verdieping') or []):
        for i,x in enumerate(p): yield ('verdieping',a,i),x,'zin',''
    for deel in('tijdlijn','fracties','college','wijken','open'):
        d=S.get(deel) or {}
        for i,x in enumerate(d.get('intro') or []): yield (deel,'intro',i),x,'zin',''
        if deel=='fracties':
            for f,F in enumerate(d.get('punten') or []):
                for i,x in enumerate(F['standpunten']): yield (deel,'punten',f,i),x,'wat','fractie: '+F['fractie']
        else:
            for i,x in enumerate(d.get('punten') or []):
                yield (deel,'punten',i),x,'wat',('datum: '+x['datum'] if x.get('datum') else '')+('wijk: '+x['wijk'] if x.get('wijk') else '')
def bronindex(urls):
    """url -> lijst (label, tekst) voor alleen de gevraagde urls."""
    I={}
    for bron in('raad','commissies'):
        meta=json.load(open(f'{DOCS}/data/{bron}/meta.json',encoding='utf8')); SPK=meta['spk']; PAR=meta['par']
        for p in sorted(glob.glob(f'{DOCS}/data/{bron}/20*.zst')):
            Y=zload(p); S=Y['s']
            for i,t in enumerate(S['t']):
                if not t: continue
                M=Y['M'][S['m'][i]]; u='https://gemeenteraad.rotterdam.nl/Agenda/Index/'+M[1] if M[1] else ''
                if u not in urls: continue
                wie=SPK[S['sp'][i]][0] if S['sp'][i]>=0 else 'onbekend'
                I.setdefault(u,[]).append((wie+(' ('+PAR[S['pa'][i]]+')' if S['pa'][i]>=0 else '')+(' · auto' if S['k'][i]==4 else ''),t))
    for key,so,datum,titel,wie,url,t in T.bronnen():
        if url in urls: I.setdefault(url,[]).append((so+' · '+ws(titel)[:100]+(' · '+ws(wie)[:60] if wie else ''),t))
    ST=zload(f'{DOCS}/data/ibabs/stukken.zst'); SO=ST['soorten']
    for r in ST['s']:
        u=r[7] if r[7].startswith('http') else 'https://gemeenteraad.rotterdam.nl/Reports/Item/'+r[7]
        if u in urls: I.setdefault(u,[]).append((SO[r[0]]+' · '+ws(r[2])[:100]+' · '+ws(r[3])[:60],r[6]))
    return I
def context(cands,cit,breed=1600):
    w=re.findall(r'\w+',cit)
    for n in(6,4,3):
        if len(w)<n: continue
        rx=re.compile(r'\W+'.join(map(re.escape,w[:n])),re.I)
        for lab,t in cands:
            m=rx.search(t)
            if m:
                a=max(0,m.start()-breed//2); b=min(len(t),m.start()+breed//2+len(cit))
                return lab,('…' if a else '')+ws(t[a:b])+('…' if b<len(t) else '')
    return None,None
def maak_in(slugs):
    os.makedirs(AD,exist_ok=True)
    SS={s:json.load(open(os.path.join(SD,s+'.json'),encoding='utf8')) for s in slugs}
    urls={x.get('url') for S in SS.values() for _,x,_,_ in punten(S)}
    I=bronindex(urls); mis=0
    for s,S in SS.items():
        out=[f'# Controle samenvatting: {S["onderwerp"]}','']
        for n,(pad,x,veld,extra) in enumerate(punten(S),1):
            lab,ctx=context(I.get(x.get('url'),[]),x.get('citaat',''))
            if not ctx: mis+=1
            out+=[f'## [{n}] {pad[0]}{" · "+extra if extra else ""}',f'ZIN: {x[veld]}',f'BRON: {x.get("bron_label","")} · {x.get("bron_datum","")}{" · automatische ondertiteling" if x.get("auto") else ""}',
                  f'CITAAT: {x.get("citaat","")}',f'CONTEXT ({lab or "niet teruggevonden"}): {ctx or "-"}','']
        open(os.path.join(AD,f'in_{s}.md'),'w',encoding='utf8').write('\n'.join(out))
        print(s,n,'punten')
    print('context niet gevonden:',mis)
def toepassen(s):
    p=os.path.join(SD,s+'.json'); S=json.load(open(p,encoding='utf8'))
    O={int(o['n']):o for o in json.load(open(os.path.join(AD,f'oordeel_{s}.json'),encoding='utf8'))}
    weg=set(); tel={'ok':0,'te_ruim':0,'onjuist':0,'toeschrijving':0}
    for n,(pad,x,veld,_) in enumerate(punten(S),1):
        o=O.get(n) or {'oordeel':'ok'}; k=o['oordeel'] if o['oordeel'] in tel else 'ok'; tel[k]+=1
        if k in('onjuist','toeschrijving'): weg.add(id(x))
        elif k=='te_ruim' and ws(o.get('nieuw')): x[veld]=ws(o['nieuw'])
    f=lambda L:[x for x in L if id(x) not in weg]
    S['kern']=f(S.get('kern') or []); S['verdieping']=[q for q in (f(p) for p in S.get('verdieping') or []) if q]
    for deel in('tijdlijn','fracties','college','wijken','open'):
        d=S.get(deel)
        if not d: continue
        d['intro']=f(d.get('intro') or [])
        if deel=='fracties': d['punten']=[F for F in ({**F,'standpunten':f(F['standpunten'])} for F in d.get('punten') or []) if F['standpunten']]
        else: d['punten']=f(d.get('punten') or [])
    S['controle']={'datum':datetime.date.today().isoformat(),**tel}
    json.dump(S,open(p,'w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
    print(s,tel)
if __name__=='__main__':
    if sys.argv[1]=='in': maak_in(sys.argv[2:] or sorted(os.path.basename(p)[:-5] for p in glob.glob(SD+'/*.json') if not p.endswith('index.json')))
    elif sys.argv[1]=='toepassen':
        for s in sys.argv[2:]: toepassen(s)
