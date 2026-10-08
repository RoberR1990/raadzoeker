# Coalitieakkoord 2026-2030 'Vaart maken' (PRO, D66, VVD, CDA, Volt): invoer voor een AI-samenvatting, controle en publicatie.
#   python src/akkoord.py in        -> WERK/akkoord/in.md (per pagina een broncode A<blz>)
#   (opdracht src/akkoord_prompt.md, één Opus-agent) -> WERK/akkoord/uit.json
#   python src/akkoord.py check     -> controleert elk citaat woordelijk op de genoemde pagina; schrijft docs/akkoord.json
#   python src/akkoord.py passages  -> letterlijke passages per voorbeelddossier (showcase.CONFIG), voor in d/<slug>-extra.json
# Bron: de pdf zoals gedeeld met de wijkraden (wijkraad.rotterdam.nl), WERK/akkoord/coalitieakkoord-2026-2030.pdf.
import json,os,re,sys
from paden import WERK,DOCS
from dossier_check import norm

D=os.path.join(WERK,'akkoord')
URL='https://wijkraad.rotterdam.nl/Document/View/13f4b9e2-cdeb-47ee-9004-face340c97aa'
TITEL="Coalitieakkoord 2026-2030 'Vaart maken'"
def paginas():
    P=json.load(open(os.path.join(D,'paginas.json'),encoding='utf8'))
    return [re.sub(r'[ \t]+',' ',re.sub('­\\s*','',p)).strip() for p in P]   # zacht afbreekstreepje met regeleinde weg
def maak_in():
    P=paginas(); out=[f'# {TITEL}','Elke pagina heeft een code A<paginanummer>.','']
    for i,p in enumerate(P,1):
        if len(p)>80: out+=[f'[A{i}]',re.sub(r'\n(?=[a-z])',' ',p),'']
    open(os.path.join(D,'in.md'),'w',encoding='utf8').write('\n'.join(out)); print(len(out),'regels')
def check():
    P=paginas(); NP={f'A{i}':norm(p) for i,p in enumerate(P,1)}
    U=json.load(open(os.path.join(D,'uit.json'),encoding='utf8')); weg=[]; tel={}
    def ok(x,deel):
        c=(x.get('bron') or '').strip(); cit=norm(x.get('citaat',''))
        good=c in NP and len(cit.split())>=4 and cit in NP[c]
        a,n=tel.get(deel,(0,0)); tel[deel]=(a+good,n+1)
        if not good: weg.append((deel,c,x.get('citaat','')[:80])); return None
        return dict(x,blz=int(c[1:]),url=URL+'#page='+c[1:],bron_label=TITEL+', blz. '+c[1:],bron_datum='2026-07-15')
    L=lambda xs,deel:[y for y in (ok(x,deel) for x in xs or []) if y]
    out={'titel':TITEL,'url':URL,'partijen':U.get('partijen',[]),'kern':L(U.get('kern'),'kern'),
         'hoofdstukken':[{'titel':h['titel'],'intro':L(h.get('intro'),'hoofdstuk'),'punten':L(h.get('punten'),'punt')} for h in U.get('hoofdstukken',[])],
         'domeinen':{k:L(v,'domein') for k,v in (U.get('domeinen') or {}).items()},'geld':L(U.get('geld'),'geld')}
    for w in weg: print(' weg',*w)
    print({k:f'{a}/{n}' for k,(a,n) in tel.items()})
    oud=os.path.join(DOCS,'akkoord.json')
    if os.path.exists(oud): out['dossiers']=json.load(open(oud,encoding='utf8')).get('dossiers',{})   # 'dossiers' blijft staan
    json.dump(out,open(os.path.join(DOCS,'akkoord.json'),'w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
def passages(rx,n=10):
    """letterlijke opsommingspunten en alinea's uit het akkoord die het zoekpatroon raken: [[tekst, blz]]"""
    from ontwerp_data import fold
    P=paginas(); uit=[]
    dicht={i:len(re.findall(rx,fold(p))) for i,p in enumerate(P,1)}   # pagina's waar het onderwerp veel terugkomt eerst
    for i,p in enumerate(P,1):
        for stuk in re.split(r'\n\s*•\s*|\n(?=[A-Z][^\n]{0,60}\n)',p):
            t=re.sub(r'^(Coalitieakkoord 2026-2030 )?Vaart maken\s*','',re.sub(r'\s*\n\s*',' ',stuk).strip())
            h=len(re.findall(rx,fold(t)))
            if 40<len(t)<900 and h: uit.append([t,i,h*10+dicht[i]])
    uit=sorted(sorted(uit,key=lambda x:-x[2])[:n],key=lambda x:x[1])   # de meest relevante, in volgorde van het akkoord
    return [[t,i] for t,i,_ in uit]
def dossiers():
    """korte AI-opsomming per voorbeelddossier (uit_dossiers.json), citaten gecontroleerd; komt in akkoord.json onder 'dossiers'"""
    P=paginas(); NP={f'A{i}':norm(p) for i,p in enumerate(P,1)}
    U=json.load(open(os.path.join(D,'uit_dossiers.json'),encoding='utf8')); A=json.load(open(os.path.join(DOCS,'akkoord.json'),encoding='utf8'))
    A['dossiers']={}
    for slug,xs in U.items():
        ok=[]
        for x in xs:
            c=x.get('bron',''); cit=norm(x.get('citaat',''))
            if c in NP and len(cit.split())>=4 and cit in NP[c]: ok.append(dict(x,blz=int(c[1:]),url=URL+'#page='+c[1:],bron_label=TITEL+', blz. '+c[1:],bron_datum='2026-07-15'))
            else: print(' weg',slug,c,x.get('citaat','')[:70])
        A['dossiers'][slug]=ok; print(slug,len(ok),'van',len(xs))
    json.dump(A,open(os.path.join(DOCS,'akkoord.json'),'w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
if __name__=='__main__':
    a=sys.argv[1] if len(sys.argv)>1 else 'in'
    if a=='in': maak_in()
    elif a=='check': check()
    elif a=='dossiers': dossiers()
    elif a=='passages':
        import showcase
        for s,c in showcase.CONFIG.items(): print(s,[(p[1],p[0][:80]) for p in passages(c['rx'])])
