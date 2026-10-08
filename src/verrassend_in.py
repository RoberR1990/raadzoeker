# Verrassende verbanden, stap 1 (zonder AI): kandidaatparen uit de Verkenner met fragmenten waarin ze samen staan.
#   python src/verrassend_in.py  -> WERK/verrassend/in.md (voor de redactionele keuze) en WERK/verrassend/kand.json
# Kandidaat = verband uit verkenner.json met genoeg samen (c>=10), beide begrippen vaak genoeg (n>=60), domeinprofielen
# verschillend (cosinus <0.6) en weinig gedeelde buren (Jaccard laag). Geen plekken, straten, woorden met hoofdletters,
# varianten van hetzelfde woord of vaste combinaties (bijna altijd samen). Fragmenten: tekstvenster (ca. 400 tekens) uit
# debat of stuk waarin beide begrippen staan; geen insprekers. Broncode D<beurt> (debat-index) of S<stuk> (tekst-index).
import json,os,re,math,collections,sys
import numpy as np
from paden import DOCS,WERK
import teksten as T, onderwerpen as OW
import verkenner as VK
from dossier_data import slug as SLUG
NPAAR=300; VENSTER=400; NFRAG=3
STRAAT=re.compile(r'(straat|weg|plein|laan|singel|kade|dijk|park|hof|dreef|haven|brug|tunnel|buurt|kwartier|polder|plaat|waard|gracht|plas|eiland|boulevard|wal|steeg)$')

def kandidaten(d):
    K=d['knopen']; buren=collections.defaultdict(set)
    for a,b,w,c in d['e']: buren[a].add(b); buren[b].add(a)
    def plek(k):
        if k['s']=='p' or STRAAT.search(k['l'].lower()) or any(ch.isupper() for ch in k['l']): return True
        g=k['g']; return sum(g)>0 and max(g)/sum(g)>0.5
    def cos(x,y):
        x=np.array(x,float); y=np.array(y,float); return float(x@y/(np.linalg.norm(x)*np.linalg.norm(y)+1e-9))
    uit=[]
    for a,b,w,c in d['e']:
        A,B=K[a],K[b]
        if c<10 or A['n']<60 or B['n']<60 or plek(A) or plek(B): continue
        la,lb=A['l'].lower(),B['l'].lower()
        if la[:5]==lb[:5] or la in lb or lb in la: continue
        if c/min(A['n'],B['n'])>0.3: continue
        cs=cos(A['dm'],B['dm'])
        if cs>=0.6: continue
        na,nb=buren[a]-{b},buren[b]-{a}; jac=len(na&nb)/max(1,len(na|nb))
        if jac>0.2: continue
        uit.append((w*math.log(c)*(1-cs)*(1-jac),a,b,w,c,cs,jac))
    uit.sort(reverse=True); return uit[:NPAAR]

def main():
    d=json.load(open(os.path.join(DOCS,'verkenner.json'),encoding='utf8')); K=d['knopen']
    vb=json.load(open(os.path.join(DOCS,'verkenner-vb.json'),encoding='utf8'))
    kand=kandidaten(d); print(len(kand),'kandidaatparen')
    # herkenning per knoop: woordstam, of zoekpatroon bij een onderwerp
    OND={SLUG(n):pp for n,pp in OW.actief()}
    import showcase as SC; OND['parkeren']=[SC.CONFIG['parkeren']['rx']]
    nodig={i for _,a,b,*_ in kand for i in (a,b)}
    stam={i:K[i]['id'][2:] for i in nodig if K[i]['id'].startswith('w:')}
    orx={i:re.compile(r'\b(?:'+'|'.join(OND[K[i]['slug']])+')') for i in nodig if K[i]['id'].startswith('o:')}
    perstam=collections.defaultdict(list)
    for i,s in stam.items(): perstam[s].append(i)
    paren=collections.defaultdict(list)   # knoop -> paren waar hij in zit
    for pi,(_,a,b,*_) in enumerate(kand): paren[a].append(pi); paren[b].append(pi)
    frag=collections.defaultdict(list); aantal=collections.Counter()
    dm=VK.zload(os.path.join(DOCS,'data','debat','meta.zst')); PAR=dm['par']; DOM=dm['dom']
    for bron,i,y,dd,g,f,x,meta in VK.eenheden():
        if bron=='d' and (not meta[2] or meta[2].lower().startswith('inspreker')): continue
        t=re.sub(r'\s+',' ',VK.tekst(x)); ft=T.fold(t)
        if len(ft)!=len(t): ft=None
        pos=collections.defaultdict(list)   # knoop -> posities in t
        for m in re.finditer(r'[^\W\d_]+',t):
            for n in perstam.get(T.stam(T.fold(m.group())),()): pos[n].append(m.start())
        if orx and ft:
            for n,rx in orx.items():
                for m in rx.finditer(ft): pos[n].append(m.start())
        if len(pos)<2: continue
        gezien=set()
        for n in pos:
            for pi in paren[n]:
                if pi in gezien: continue
                _,a,b,*_=kand[pi]
                if a not in pos or b not in pos: continue
                best=min(((abs(p-q),p,q) for p in pos[a] for q in pos[b]),default=None)
                if not best or best[0]>VENSTER: continue
                gezien.add(pi); aantal[pi]+=1
                lo,hi=min(best[1],best[2]),max(best[1],best[2]); mid=(lo+hi)//2
                s0=max(0,min(lo-80,mid-200)); s1=min(len(t),max(hi+120,mid+200))
                s0=t.rfind(' ',0,s0)+1 if s0 else 0; e=t.find(' ',s1); s1=len(t) if e<0 else e
                tekst=('…' if s0 else '')+t[s0:s1].strip()+('…' if s1<len(t) else '')
                if bron=='d':
                    V,A,wie,U=meta; info={'code':f'D{i}','datum':V[0],'verg':V[2],'punt':A[2][:140],'fractie':PAR[f] if f>=0 else '','wie':'college/voorzitter' if f<0 else 'raadslid'}
                else:
                    r=meta[0]; info={'code':f'S{i}','datum':r[1],'verg':'','punt':r[2][:140],'fractie':'','wie':'stuk'}
                info['t']=tekst; frag[pi].append(info)
    os.makedirs(os.path.join(WERK,'verrassend'),exist_ok=True)
    md=['# Verrassende verbanden: kandidaten',f'{len(kand)} paren uit verkenner.json (c>=10, n>=60, cos domein <0.6, weinig gedeelde buren). '
        'Per paar: domeinen, aantal vensters samen (c), eenheden met beide binnen 400 tekens, jaren 2018-2026 per begrip, 3 fragmenten met broncode.','']
    out=[]
    for pi,(sc,a,b,w,c,cs,jac) in enumerate(kand):
        A,B=K[a],K[b]; F=frag[pi]
        # spreiding: liefst verschillende jaren, debat en stuk door elkaar, nieuwste eerst
        F.sort(key=lambda r:r['datum'],reverse=True); kies=[]; jr=set()
        for r in F:
            if r['datum'][:4] not in jr: kies.append(r); jr.add(r['datum'][:4])
            if len(kies)==NFRAG: break
        for r in F:
            if len(kies)>=NFRAG: break
            if r not in kies: kies.append(r)
        dom=lambda k:DOM[k['dom']][1]
        md+=[f'## P{pi:03d} · {A["l"]} + {B["l"]}',
             f'- id: `{A["id"]}` + `{B["id"]}` · domeinen: {dom(A)} × {dom(B)} · c={c} · samen in {aantal[pi]} eenheden · n={A["n"]}/{B["n"]} · npmi={w} · cos={cs:.2f} · jac={jac:.2f}',
             f'- jaren {A["l"]}: {A["j"]} · {B["l"]}: {B["j"]}']
        for r in kies:
            wie=r['fractie'] or r['wie']
            md.append(f'- [{r["code"]}] {r["datum"]} {r["verg"]} · {wie} · {r["punt"]}\n  > {r["t"]}')
        if not kies: md.append('- (geen fragment gevonden)')
        md.append('')
        out.append({'p':pi,'a':A['id'],'b':B['id'],'la':A['l'],'lb':B['l'],'c':c,'samen':aantal[pi],'frag':kies})
    open(os.path.join(WERK,'verrassend','in.md'),'w',encoding='utf8').write('\n'.join(md))
    json.dump(out,open(os.path.join(WERK,'verrassend','kand.json'),'w',encoding='utf8'),ensure_ascii=False,indent=0)
    print('geschreven:',os.path.join(WERK,'verrassend','in.md'),sum(1 for o in out if o['frag']),'paren met fragment')
if __name__=='__main__': main()
