# Fase 4: gegevens voor het Lab, zo dat elke grafiek in de pagina zelf te filteren is op domein, gebied, fractie en periode.
#   python src/lab_data.py  -> docs/lab2.json
# r: één rij per motie, toezegging en schriftelijke vraag sinds 2018:
#    [soort 0 motie / 1 toezegging / 2 vraag, datum, domein (-1), gebieden (bitmasker), fractie (-1), [mede-fracties], status, collegelid (-1), doorlooptijd in dagen (-1), over de termijn 0/1]
#    status: 1 aangenomen, 2 verworpen, 3 ingetrokken/aangehouden, 4 open, 5 afgedaan, 0 overig
# w: gesproken woorden in de raad per [jaar, domein, fractie] (agendapunten met een domeinlabel)
import json,os,re,glob,collections,datetime
from paden import WERK,DOCS,STAND
import domeinen as D
from ontwerp_data import zload,iso

ALIAS={'GL':'GroenLinks','VOLT':'Volt','Bij1':'BIJ1'}
def main():
    LD=json.load(open(os.path.join(WERK,'labels','domein.json'),encoding='utf8'))
    LG=json.load(open(os.path.join(WERK,'labels','gebied.json'),encoding='utf8'))
    INFO=json.load(open(os.path.join(WERK,'labels','info.json'),encoding='utf8'))
    GB=json.load(open(os.path.join(WERK,'gebied','gebieden.json'),encoding='utf8'))['gebieden']
    ouder={r['id']:r['ouder'] for r in GB}; GN={r['id']:r['naam'] for r in GB if r['niveau']=='gebied'}; GL=sorted(GN.values())
    def gmask(k):
        gg={x[0] if x[0] in GN else ouder.get(x[0]) for x in LG.get(k,[])}; gg={GN[g] for g in gg if g in GN}
        return 0 if len(gg)>=5 else sum(1<<GL.index(g) for g in gg)
    SL=[s for s,_,_ in D.DOMEINEN]; DN=[n for _,n,_ in D.DOMEINEN]
    sleutel={}
    for k,v in INFO.items():
        m=re.search(r'/Item/([0-9a-f-]{36})',v[4] or '')
        if m: sleutel[m.group(1)]=k
    L=json.load(open(os.path.join(WERK,'ibabs','lijsten.json'),encoding='utf8'))
    mede={r['DT_RowId']:[x.strip() for x in re.split(r'[;,\n]',r.get('medeindiendepartijen') or '') if x.strip()] for r in L['moties']}
    ST=zload(os.path.join(DOCS,'data','ibabs','stukken.zst')); S=ST['soorten']
    FR=[];CL=[]
    def idx(lst,x):
        if not x: return -1
        if x not in lst: lst.append(x)
        return lst.index(x)
    rows=[]
    for r in ST['s']:
        so={'Motie':0,'Toezegging':1,'Schriftelijke vragen':2}.get(S[r[0]])
        if so is None or r[1]<'2018': continue
        k=sleutel.get(r[7]); d=LD.get(k,[None])[0] if k else None
        wie=r[3]; fr=cl=-1; md=[]
        if so in(0,2):
            p=wie.split('(')[0].split('\n')[0].strip(); p=ALIAS.get(p,p); fr=idx(FR,p)
            md=[idx(FR,ALIAS.get(x,x)) for x in mede.get(r[7],[]) if ALIAS.get(x,x)!=p]
        else:
            c=re.sub(r'\s*\(.*','',wie.split(' · ')[0].split('\n')[0]).strip(); cl=idx(CL,c) if c and not c.startswith('·') else -1
        af=iso((re.search(r'(?:afgedaan|beantwoord) ([\d-]+)',r[5]) or [None,''])[1]); dv=iso((re.search(r'verwacht ([\d-]+)',r[5]) or [None,''])[1])
        door=(datetime.date.fromisoformat(af)-datetime.date.fromisoformat(r[1])).days if af else -1
        laat=1 if (r[4]==4 and dv and dv<STAND) or (af and dv and af>dv) else 0
        rows.append([so,r[1],SL.index(d) if d in SL else -1,gmask(k) if k else 0,fr,md,r[4],cl,door,laat])
    # woorden per jaar, domein, fractie (raad)
    meta=json.load(open(os.path.join(DOCS,'data','raad','meta.json'),encoding='utf8')); PAR=meta['par']
    w=collections.Counter()
    for p in sorted(glob.glob(os.path.join(DOCS,'data','raad','*.zst'))):
        y=os.path.basename(p)[:4]; Y=zload(p); s=Y['s']
        for j,t in enumerate(s['t']):
            if s['k'][j] not in(0,4) or not t or s['pa'][j]<0: continue
            d=LD.get(f'r:{y}:{s["i"][j]}',[None])[0]
            w[(y,SL.index(d) if d in SL else -1,idx(FR,ALIAS.get(PAR[s['pa'][j]],PAR[s['pa'][j]])))]+=len(t.split())
    out={'stand':STAND,'dom':[[s,n] for s,n in zip(SL,DN)],'geb':GL,'fr':FR,'cl':CL,'r':rows,'w':[[y,d,f,n] for (y,d,f),n in w.items()]}
    p=os.path.join(DOCS,'lab2.json'); json.dump(out,open(p,'w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
    print(len(rows),'rijen',len(FR),'fracties',len(CL),'collegeleden',os.path.getsize(p)//1000,'kB')

if __name__=='__main__': main()
