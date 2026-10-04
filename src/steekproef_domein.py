# Fase 1 controle: beoordelingspagina voor de domeinlabels.
#   python src/steekproef_domein.py  -> ontwerp/steekproef-domein.html (los te openen, niet op de site)
# Tabblad 1: gelaagde steekproef van 200 (per methode, zodat de precisie per methode meetbaar is; weging naar de populatie achteraf).
# Tabblad 2: alle stukken en agendapunten met 'parkeer'/'parkeren' in de titel.
import json,os,random,re,collections
from paden import WERK,ROOT
import domeinen as D

LAGEN=[('bron',60),('woordmodel-stuk',50),('woordmodel-debat',40),('gekoppeld',25),('geen',25)]

def laag(k,v):
    if v[0] is None: return 'geen'
    if v[1]=='woordmodel': return 'woordmodel-debat' if k[0] in 'rc' else 'woordmodel-stuk'
    return v[1]

def main():
    L=json.load(open(os.path.join(WERK,'labels','domein.json'),encoding='utf8'))
    I=json.load(open(os.path.join(WERK,'labels','info.json'),encoding='utf8'))
    per=collections.defaultdict(list)
    for k,v in L.items(): per[laag(k,v)].append(k)
    random.seed(2026); rows=[]
    for n,a in LAGEN:
        for k in random.sample(sorted(per[n]),a): rows.append(k)
    random.shuffle(rows)
    pk=sorted((k for k in I if re.search(r'parkeer|parkeren',I[k][2] or '',re.I)),key=lambda k:(L[k][0]=='mobiliteit',I[k][1]),reverse=False)
    def rij(k): s,d,t,w,u=I[k]; v=L[k]; return [k,s,d,t,w,u,v[0] or 'geen',v[1],v[2],laag(k,v)]
    data={'domeinen':[[s,n] for s,n,_ in D.DOMEINEN]+[['geen','Geen domein (procedureel)']],
          'steekproef':[rij(k) for k in rows],'parkeren':[rij(k) for k in pk],
          'populatie':{n:len(per[n]) for n,_ in LAGEN}}
    html=open(os.path.join(os.path.dirname(__file__),'steekproef_domein.tpl.html'),encoding='utf8').read()
    out=os.path.join(ROOT,'ontwerp','steekproef-domein.html')
    open(out,'w',encoding='utf8').write(html.replace('/*DATA*/null',json.dumps(data,ensure_ascii=False)))
    print(out,len(rows),len(pk),data['populatie'])

if __name__=='__main__': main()
