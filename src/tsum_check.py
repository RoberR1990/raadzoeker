# Controle van themasamenvattingen met citaten (zie data/tsum/INSTRUCTIES.md).
#   python src/tsum_check.py 24 25 ...         toets WERK/tsum/out_tNN.json tegen WERK/tsum/in_tNN.txt
#   python src/tsum_check.py --schrijf 24 ...   idem, en zet de goedgekeurde versie in data/tsum/out_BB.json
# Regels: een ontwikkeling of standpunt blijft alleen staan als het citaat letterlijk in de bron staat;
# bij een standpunt bovendien in een fragment van die fractie/persoon. Eigennamen in kern/recent die niet
# in de bron staan worden gemeld (niet automatisch geschrapt).
import json,re,sys,os
from paden import DATA,WERK
BATCH={24:'08',25:'08',26:'08',30:'10',31:'10',32:'10',33:'11',34:'11',35:'11',36:'12',37:'12',38:'12',39:'13',40:'13'}
def n(s): return re.sub(r'\s+',' ',s.replace('’',"'").replace('‘',"'").replace('“','"').replace('”','"')).strip().lower().strip('.…"\' ')
def toets(i):
    src=open(f'{WERK}/tsum/in_t{i}.txt',encoding='utf8').read()
    lines=[l for l in src.split('\n') if l.startswith('[')]
    S=n(src)
    d=json.load(open(f'{WERK}/tsum/out_t{i}.json',encoding='utf8'))[0]; assert d['id']==i
    weg=[]
    def ok(x,wie=None):
        q=n(x.get('citaat',''))
        if len(q.split())<5 or q not in S: return False
        if wie:
            key=n(wie.split(' (')[0].split(',')[0])
            return any(q in n(l) and key in n(l) for l in lines)
        return True
    o2=[x for x in d['ontwikkeling'] if ok(x)]; weg+=[('ontwikkeling',x['periode']) for x in d['ontwikkeling'] if x not in o2]
    s2=[x for x in d['standpunten'] if ok(x,x['wie'])]; weg+=[('standpunt',x['wie']) for x in d['standpunten'] if x not in s2]
    d['ontwikkeling'],d['standpunten']=o2,s2
    los=sorted({t for t in re.findall(r'\b[A-Z][a-zà-ÿ]{3,}(?:[- ][A-Z][a-zà-ÿ]+)*',d['kern']+' '+d.get('recent','')) if t.lower() not in src.lower()})
    print(i,f"ontw {len(o2)} standp {len(s2)} | geschrapt: {weg} | onbekende woorden kern/recent: {los}")
    return d
if __name__=='__main__':
    schrijf='--schrijf' in sys.argv; ids=[int(x) for x in sys.argv[1:] if x!='--schrijf']
    res={i:toets(i) for i in ids}
    if schrijf:
        for bb in sorted({BATCH[i] for i in ids}):
            f=f'{DATA}/tsum/out_{bb}.json'; L=json.load(open(f,encoding='utf8')) if os.path.exists(f) else []
            L=[res.get(d['id'],d) for d in L]+[res[i] for i in ids if BATCH[i]==bb and i not in {d['id'] for d in L}]
            json.dump(sorted(L,key=lambda d:d['id']),open(f,'w',encoding='utf8'),ensure_ascii=False,indent=1)
        print('geschreven')
