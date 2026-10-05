# Overlap tussen thema's: welk deel van de stukken en debatbeurten van thema A valt ook onder thema B?
#   python src/thema_overlap.py            -> de thema's 'dwars door de organisatie' uit themes.py
#   (import) overlap(defs)                 -> defs = [(naam, 'term | term ...')]
# Stuk hoort bij een thema als een term in de titel staat of minstens 3x in de tekst (zoals ontwerp_data.py); debatbeurt bij 1 treffer.
import json,os,glob,collections
from paden import DOCS
from ontwerp_data import zload, fold, rx
import themes

def sets(defs):
    R=[rx(t) if isinstance(t,str) else t for _,t in defs]; S=[set() for _ in defs]
    ST=zload(f'{DOCS}/data/ibabs/stukken.zst')
    for i,r in enumerate(ST['s']):
        ft=fold(r[2]); fx=fold(r[6][:6000])
        for k,rr in enumerate(R):
            if rr.search(ft) or len(rr.findall(fx))>=3: S[k].add(('s',i))
    dm=zload(f'{DOCS}/data/debat/meta.zst'); B=dm['blok']
    for p in sorted(glob.glob(f'{DOCS}/data/debat/b/*.zst')):
        blk=zload(p); b0=int(os.path.basename(p)[:4])*B
        for j,segs in enumerate(blk):
            t=fold(' '.join(s for _,s in segs))
            for k,rr in enumerate(R):
                if rr.search(t): S[k].add(('d',b0+j))
    return S

def overlap(defs):
    S=sets(defs); n=len(defs)
    print('aantal:',{defs[k][0]:len(S[k]) for k in range(n)})
    paren=[]
    for a in range(n):
        for b in range(a+1,n):
            i=len(S[a]&S[b]);
            if not i: continue
            paren.append((round(i/min(len(S[a]),len(S[b])),2),round(i/len(S[a]|S[b]),2),defs[a][0],defs[b][0],i))
    for p in sorted(paren,reverse=True)[:20]: print(p)
    return S

if __name__=='__main__':
    import sys,onderwerpen as OW
    if sys.argv[1:2]==['nieuw']: overlap([(n,OW.rx(pp)) for n,pp,_ in OW.DWARS]); sys.exit()
    g=next(g for g in themes.T if 'dwars' in g[0].lower())
    overlap([(t[0],t[1]) for t in g[1] if t[0]!='Toezeggingen'])
