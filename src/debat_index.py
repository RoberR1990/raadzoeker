# Zoekindex over alles wat er in debatten is gezegd (raad: notulen 2018-2026; commissies: ondertiteling 2022-2026) -> docs/data/debat/
# Eenheid = wat één spreker bij één agendapunt zei ('beurt'). Licht genoeg voor een telefoon: alleen de shards die een zoekopdracht raakt worden geladen.
#   meta.zst   {verg:[[datum, bron 0 raad/1 commissie, naam vergadering, agendaId, videoref]],
#               ap:[[verg, nr, titel, domein (-1), gebieden-bitmasker]], spk:[naam], par:[fractie], dom:[[slug,naam]], geb:[naam],
#               u:[[ap, spreker (-1), fractie (-1), woorden, automatische ondertiteling 0/1]], ni, blok, stand}
#   i/NNN.zst  {stam:[[beurt-delta,...],[tf,...]]}  (zelfde stam- en hashregels als teksten.py en zoek.html)
#   b/NNN.zst  per blok van BLOK beurten: [[[seconde in de video, tekst], ...], ...]
import json,os,re,glob,collections,zstandard
from paden import WERK,DOCS,STAND
import teksten as T, domeinen as D
from ontwerp_data import zload
from dossier_data import slug
OUT=os.path.join(DOCS,'data','debat'); NI=512; BLOK=48

def main():
    os.makedirs(os.path.join(OUT,'i'),exist_ok=True); os.makedirs(os.path.join(OUT,'b'),exist_ok=True)
    LD=json.load(open(os.path.join(WERK,'labels','domein.json'),encoding='utf8'))
    LG=json.load(open(os.path.join(WERK,'labels','gebied.json'),encoding='utf8'))
    GB=json.load(open(os.path.join(WERK,'gebied','gebieden.json'),encoding='utf8'))['gebieden']
    ouder={r['id']:r['ouder'] for r in GB}; GN={r['id']:r['naam'] for r in GB if r['niveau']=='gebied'}; GL=sorted(GN.values())
    SL=[s for s,_,_ in D.DOMEINEN]
    def gmask(k):
        gg={x[0] if x[0] in GN else ouder.get(x[0]) for x in LG.get(k,[])}; gg={GN[g] for g in gg if g in GN}
        return 0 if len(gg)>=5 else sum(1<<GL.index(g) for g in gg)
    verg=[];ap=[];u=[];tekst=[];SPK=[];PAR=[]
    def idx(l,x):
        if x not in l: l.append(x)
        return l.index(x)
    for bron,pre in(('raad','r'),('commissies','c')):
        meta=json.load(open(os.path.join(DOCS,'data',bron,'meta.json'),encoding='utf8'))
        for p in sorted(glob.glob(os.path.join(DOCS,'data',bron,'20*.zst'))):
            y=os.path.basename(p)[:4]; Y=zload(p); S=Y['s']
            vi={}; ai={}; beurt={}
            for j,t in enumerate(S['t']):
                if S['k'][j] not in(0,4) or not t: continue
                m=S['m'][j]; i=S['i'][j]
                if m not in vi:
                    M=Y['M'][m]; vi[m]=len(verg); verg.append([M[0],0 if pre=='r' else 1,M[2] or ('Gemeenteraad' if pre=='r' else ''),M[1] or '',M[4] if len(M)>4 else ''])
                if i not in ai:
                    I=Y['I'][i]; k=f'{pre}:{y}:{i}'; d=LD.get(k,[None])[0]
                    ai[i]=len(ap); ap.append([vi[m],I[1],re.sub(r'\s+',' ',I[2])[:200],SL.index(d) if d in SL else -1,gmask(k)])
                sp=S['sp'][j]; pa=S['pa'][j]
                naam=meta['spk'][sp][0] if sp>=0 else ''
                key=(ai[i],naam)
                if key not in beurt:
                    beurt[key]=len(u); u.append([ai[i],idx(SPK,naam) if naam else -1,idx(PAR,meta['par'][pa]) if pa>=0 else -1,0,1 if S['k'][j]==4 else 0]); tekst.append([])
                b=beurt[key]; tekst[b].append([S['v'][j] if S['v'][j] is not None else -1,t]); u[b][3]+=len(t.split())
                if S['k'][j]==0: u[b][4]=0
        print(bron,len(u),'beurten tot nu')
    post=collections.defaultdict(list)
    for b,segs in enumerate(tekst):
        for w,c in collections.Counter(T.woorden(' '.join(t for _,t in segs))).items(): post[w].append((b,min(c,255)))
    n=len(u); grens=n*0.35
    shards=[{} for _ in range(NI)]
    for w,p in post.items():
        if len(p)>grens: continue
        ds=[p[0][0]]+[p[k][0]-p[k-1][0] for k in range(1,len(p))]
        shards[T.h(w)][w]=[ds,[c for _,c in p]]
    zc=zstandard.ZstdCompressor(level=19); tot=0
    def schrijf(p,obj):
        nonlocal tot
        b=zc.compress(json.dumps(obj,ensure_ascii=False,separators=(',',':')).encode('utf8'))
        if not os.path.exists(p) or open(p,'rb').read()!=b: open(p,'wb').write(b)
        tot+=len(b)
    for k,sh in enumerate(shards): schrijf(os.path.join(OUT,'i',f'{k:03d}.zst'),sh)
    for b in range(0,n,BLOK): schrijf(os.path.join(OUT,'b',f'{b//BLOK:04d}.zst'),tekst[b:b+BLOK])
    schrijf(os.path.join(OUT,'meta.zst'),{'verg':verg,'ap':ap,'spk':SPK,'par':PAR,'dom':[[slug(n),n] for _,n,_ in D.DOMEINEN],'geb':GL,'u':u,'ni':NI,'blok':BLOK,'stand':STAND})
    print(n,'beurten',len(ap),'agendapunten',len(post),'stammen',round(tot/1e6,1),'MB')
if __name__=='__main__': main()
