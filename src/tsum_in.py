# Maakt invoerbestanden voor de themasamenvattingen (opdracht: data/tsum/INSTRUCTIES.md).
# Gebruik: python src/tsum_in.py 24,25,26 08   -> WERK/tsum/in_08.txt
# Per thema: zoektermen, trend per jaar en per jaar een spreiding van fragmenten rond een treffer
# (hooguit 2 per vergadering, notulen boven ondertiteling, vaste seed zodat het herhaalbaar is).
import json,sys,os,re,random,collections,zstandard
from paden import DOCS,WERK
import themes
import unicodedata
# zelfde zoeklogica als insights.py (dat script draait bij import, daarom hier herhaald)
def fold(s): return ''.join(c for c in unicodedata.normalize('NFD',s.lower()) if unicodedata.category(c)!='Mn').replace('’',"'").replace('‘',"'")
def rx(terms):
    ps=[]
    for t in terms.split('|'):
        t=t.strip(); m=re.match(r'^"(.+)"$',t); core=re.escape(fold(m.group(1) if m else t))
        ps.append(r'(?<![a-z0-9])'+core+r'(?![a-z0-9])' if m else core)
    return re.compile('|'.join(ps))
PER_JAAR=15; BREED=220
def main(ids,nn):
    meta=json.load(open(f'{DOCS}/data/raad/meta.json',encoding='utf8'))
    TH=[(g[0],t) for g in themes.T for t in g[1]]
    ins=meta['ins']; years=ins['years']; SPK=meta['spk']; PAR=meta['par']; ROLES=meta['roles']
    dz=zstandard.ZstdDecompressor()
    data={y:json.loads(dz.decompress(open(f'{DOCS}/data/raad/{y}.zst','rb').read(),max_output_size=10**9)) for y in years}
    out=[]
    for tid in ids:
        groep,t=TH[tid]; R=rx(t[1]); rnd=random.Random(tid)
        out.append(f'### THEMA id={tid} | groep: {groep} | naam: {t[0]}')
        out.append('Zoektermen: '+t[1])
        out.append('Trend (treffers per 100.000 gesproken woorden): '+', '.join(f'{y}: {v}' for y,v in zip(years,ins['ty'][tid])))
        for y in years:
            Y=data[y]; S=Y['s']; hits=[]
            for i,tx in enumerate(S['t']):
                if S['k'][i] not in(0,4) or not tx: continue
                m=R.search(fold(tx))
                if m: hits.append((i,m.start()))
            rnd.shuffle(hits); hits.sort(key=lambda h:S['k'][h[0]]!=0)   # notulen eerst, verder willekeurig
            per=collections.Counter(); kies=[]
            for i,p in hits:
                if per[S['m'][i]]>=2: continue
                per[S['m'][i]]+=1; kies.append((i,p))
                if len(kies)>=PER_JAAR: break
            kies.sort()
            out.append(f'\n## {y} ({len(hits)} spreekbeurten met treffer, {len(kies)} getoond)')
            for i,p in kies:
                tx=S['t'][i]; a=max(0,p-BREED); b=min(len(tx),p+BREED)
                frag=('…' if a else '')+re.sub(r'\s+',' ',tx[a:b]).strip()+('…' if b<len(tx) else '')
                M=Y['M'][S['m'][i]]; I=Y['I'][S['i'][i]]
                sp=SPK[S['sp'][i]][0] if S['sp'][i]>=0 else 'Onbekend'
                rol=[PAR[S['pa'][i]]] if S['pa'][i]>=0 else []
                rol.append(ROLES[S['ro'][i]])
                if S['k'][i]==4: rol.append('automatische ondertiteling')
                out.append(f"[{M[0]} | {(I[1]+' '+I[2]).strip()[:120]}] {sp} ({', '.join(rol)}): {frag}")
        out.append('\n')
    os.makedirs(f'{WERK}/tsum',exist_ok=True)
    p=f'{WERK}/tsum/in_{nn}.txt'; open(p,'w',encoding='utf8').write('\n'.join(out))
    print(p,len('\n'.join(out))//1000,'kB')
if __name__=='__main__':
    main([int(x) for x in sys.argv[1].split(',')],sys.argv[2])
