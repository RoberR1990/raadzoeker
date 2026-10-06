# Invoerpakket voor de samenvatting van één vergadering (raad of commissie), zuinig met tokens.
#   python src/verg_in.py <agendaId>  -> WERK/verg/in_<id8>.txt en WERK/verg/bron_<id8>.json (voor de citaatcontrole)
# Per agendapunt de beurten (spreker x agendapunt) uit de debatindex, met code #U<nr>, spreker, fractie en starttijd.
# Zuinig: procedurele punten (< 300 woorden) alleen als titel; per agendapunt hooguit MAXAP woorden, verdeeld over de beurten
# (elke beurt houdt begin en eind, waar meestal de kern en de conclusie staan); stopwoorden/aanloop ('voorzitter, dank u wel') eruit.
import json,os,re,sys
from paden import DOCS,WERK
from ontwerp_data import zload
MAXAP=3800; MINAP=300
AANLOOP=re.compile(r'^\s*((dank u( wel)?|dankjewel|ja|nou|goed|voorzitter|uh+|eh+)[,.!\s]*)+',re.I)
def tijd(s): s=max(0,int(s)); return f'{s//3600}:{s//60%60:02d}:{s%60:02d}'
def kort(woorden,n):
    if len(woorden)<=n: return ' '.join(woorden)
    a=int(n*.7); return ' '.join(woorden[:a])+' […] '+' '.join(woorden[-(n-a):])
def main(ag):
    D=os.path.join(DOCS,'data','debat'); m=zload(os.path.join(D,'meta.zst')); B=m['blok']
    vi=next(i for i,v in enumerate(m['verg']) if v[3]==ag); V=m['verg'][vi]
    aps=[i for i,a in enumerate(m['ap']) if a[0]==vi]; us=[i for i,u in enumerate(m['u']) if u[0] in aps]
    blok={}
    def tekst(i):
        b=i//B
        if b not in blok: blok[b]=zload(os.path.join(D,'b',f'{b:04d}.zst'))
        return blok[b][i%B]
    uit=[f'### VERGADERING {V[2]} | {V[0]} | agendaId {ag} | video {V[4]}',
         'Codes: #U<nr> = één spreker bij één agendapunt; [h:mm:ss] = moment in de video. […] = ingekort.','']
    bron={'verg':V,'u':{},'ap':{}}
    for a in aps:
        A=m['ap'][a]; ua=[i for i in us if m['u'][i][0]==a]; tot=sum(m['u'][i][3] for i in ua)
        bron['ap'][A[1]]={'titel':A[2],'dom':A[3],'geb':A[4],'u':[str(i) for i in ua]}
        uit.append(f'## {A[1]} {A[2]}' + ('' if tot>=MINAP else '  (procedureel, niet samenvatten)'))
        if tot<MINAP: continue
        budget=MAXAP
        for i in sorted(ua,key=lambda i:tekst(i)[0][0]):
            U=m['u'][i]; segs=tekst(i); wie=m['spk'][U[1]] if U[1]>=0 else 'Onbekend'; par=m['par'][U[2]] if U[2]>=0 else ''
            if wie.lower().startswith('inspreker'): wie='Inspreker'   # privacy: geen namen van insprekers
            t=AANLOOP.sub('',' '.join(s for _,s in segs)); w=t.split()
            n=max(60,int(MAXAP*U[3]/max(1,tot)))
            uit.append(f'#U{i} [{tijd(segs[0][0])}] {wie}{" ("+par+")" if par else ""}: {kort(w,n)}')
            bron['u'][str(i)]={'wie':wie,'par':par,'segs':segs}
        uit.append('')
    os.makedirs(os.path.join(WERK,'verg'),exist_ok=True); k=ag[:8]
    open(os.path.join(WERK,'verg',f'in_{k}.txt'),'w',encoding='utf8').write('\n'.join(uit))
    json.dump(bron,open(os.path.join(WERK,'verg',f'bron_{k}.json'),'w',encoding='utf8'),ensure_ascii=False)
    print(k,len('\n'.join(uit).split()),'woorden in het pakket')
if __name__=='__main__': main(sys.argv[1])
