# Data voor de ontwerpschermen Mijn dossier en Briefing -> docs/ontwerp/dossiers.json
# Per thema (41, uit themes.py): trend, partijen, collegeleden, AI-samenvatting, moties, toezeggingen,
# schriftelijke vragen, rekenkamer en de debatten waarin het thema het meest viel.
import json,os,re,collections,unicodedata,zstandard,glob
from paden import DOCS,DATA,STAND
import themes
def fold(s): return ''.join(c for c in unicodedata.normalize('NFD',s.lower()) if unicodedata.category(c)!='Mn').replace('’',"'").replace('‘',"'")
def rx(terms):
    ps=[]
    for t in terms.split('|'):
        t=t.strip(); m=re.match(r'^"(.+)"$',t); core=re.escape(fold(m.group(1) if m else t))
        ps.append(r'(?<![a-z0-9])'+core+r'(?![a-z0-9])' if m else core)
    return re.compile('|'.join(ps))
dz=zstandard.ZstdDecompressor()
def zload(p): return json.loads(dz.decompress(open(p,'rb').read(),max_output_size=10**9))
def main():
    meta=json.load(open(f'{DOCS}/data/raad/meta.json',encoding='utf8')); I=meta['ins']
    TH=[(g[0],t) for g in themes.T for t in g[1]]; R=[rx(t[1]) for _,t in TH]
    tsum={d['id']:d for f in glob.glob(f'{DATA}/tsum/out_*.json') for d in json.load(open(f,encoding='utf8'))}
    ST=zload(f'{DOCS}/data/ibabs/stukken.zst'); S=ST['soorten']
    # stukken per thema: titel telt altijd, tekst pas bij >=3 treffers (lange motieteksten raken veel thema's zijdelings)
    per=collections.defaultdict(list)
    for r in ST['s']:
        ft=fold(r[2]); fx=fold(r[6][:6000])
        for k,rr in enumerate(R):
            if rr.search(ft) or len(rr.findall(fx))>=3: per[k].append(r)
    # debatten: treffers per raadsvergadering per thema
    deb=collections.defaultdict(collections.Counter); item={}
    for p in sorted(glob.glob(f'{DOCS}/data/raad/*.zst')):
        Y=zload(p); s=Y['s']
        for i,t in enumerate(s['t']):
            if s['k'][i] not in(0,4) or not t: continue
            f=fold(t); mt=Y['M'][s['m'][i]]
            for k,rr in enumerate(R):
                c=len(rr.findall(f))
                if c:
                    key=(mt[0],mt[1] or '',Y['I'][s['i'][i]][1]+' '+Y['I'][s['i'][i]][2]); deb[k][key]+=c
    out=[]
    for k,(groep,t) in enumerate(TH):
        rs=per[k]
        def lst(soort,status=None,n=8):
            x=[r for r in rs if S[r[0]]==soort and (status is None or r[4] in status)]
            return [[r[1],r[2],r[3],r[5],r[7] if r[7].startswith('http') else 'https://gemeenteraad.rotterdam.nl/Reports/Item/'+r[7],r[8]] for r in x[:n]],len(x)
        mot_open,n_mot_open=lst('Motie',(4,),10)
        mot_aan=[r for r in rs if S[r[0]]=='Motie' and r[4] in(1,4,5)]
        toez_open,n_toez_open=lst('Toezegging',(4,),10)
        te_laat=sum(1 for r in rs if S[r[0]]=='Toezegging' and r[4]==4 and (m:=re.search(r'verwacht (\d\d)-(\d\d)-(\d{4})',r[5])) and f'{m.group(3)}-{m.group(2)}-{m.group(1)}'<STAND)
        sv,n_sv=lst('Schriftelijke vragen',None,6)
        rk,n_rk=lst('Rekenkamerrapport',None,5)
        brief,n_brief=lst('Collegebrief',None,6)
        wijk=sum(1 for r in rs if S[r[0]].startswith(('Wijk','Ongevraagd','Collegereactie')))
        top=sorted(deb[k].items(),key=lambda x:(-(x[0][0]>='2025'),-x[1]))[:6]
        ts=tsum.get(k)
        out.append({'id':k,'naam':t[0],'groep':groep,'termen':t[1],'sub':[s[0] for s in t[2]],
            'trend':I['ty'][k],'trendn':I['tyn'][k],'jaren':I['years'],
            'partijen':sorted(zip(I['parties'],I['tp'][k]),key=lambda x:-x[1]),
            'college':sorted([(c,v) for c,v in zip(I['coll'],I['tw'][k])],key=lambda x:-x[1])[:5],
            'tsum':ts,
            'moties':{'aangenomen':len(mot_aan),'open':n_mot_open,'afgedaan':sum(1 for r in mot_aan if r[4]==5),
                      'verworpen':sum(1 for r in rs if S[r[0]]=='Motie' and r[4]==2),'lijst':mot_open,
                      'perjaar':dict(collections.Counter(r[1][:4] for r in mot_aan))},
            'toez':{'open':n_toez_open,'te_laat':te_laat,'afgedaan':sum(1 for r in rs if S[r[0]]=='Toezegging' and r[4]==5),'lijst':toez_open},
            'sv':{'n':n_sv,'lijst':sv},'rekenkamer':{'n':n_rk,'lijst':rk},'brieven':{'n':n_brief,'lijst':brief},'wijk':wijk,
            'debatten':[[d,a,ti.strip()[:160],c] for (d,a,ti),c in top]})
    os.makedirs(f'{DOCS}/ontwerp',exist_ok=True)
    json.dump({'stand':STAND,'dossiers':out},open(f'{DOCS}/ontwerp/dossiers.json','w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
    print('dossiers',len(out),os.path.getsize(f'{DOCS}/ontwerp/dossiers.json')//1000,'kB')
    for d in out[:3]+out[12:14]: print(d['naam'],d['moties']['aangenomen'],d['moties']['open'],d['toez']['open'],d['toez']['te_laat'],d['sv']['n'],d['rekenkamer']['n'],d['debatten'][:1])
if __name__=='__main__': main()
