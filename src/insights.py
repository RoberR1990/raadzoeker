
import json,re,unicodedata,collections,sys
import themes
import os
OUT=os.environ.get('RZ_OUT','out'); YSEL=os.environ.get('RZ_YEARS'); SPOKEN=(4,) if OUT!='out' else (0,4)
meta=json.load(open(f'{OUT}/meta.json'))
def fold(s): return ''.join(c for c in unicodedata.normalize('NFD',s.lower()) if unicodedata.category(c)!='Mn').replace('’',"'").replace('‘',"'")
def rx(terms):
    ps=[]
    for t in terms.split('|'):
        t=t.strip()
        m=re.match(r'^"(.+)"$',t)
        core=re.escape(fold(m.group(1) if m else t))
        ps.append(r'(?<![a-z0-9])'+core+r'(?![a-z0-9])' if m else core)
    return re.compile('|'.join(ps))
TH=[t for g in themes.T for t in g[1]]
R=[rx(t[1]) for t in TH]
years=[y['y'] for y in meta['years'] if not YSEL or y['y'] in YSEL.split(',')]
PAL=meta['par']
hy=[collections.Counter() for _ in TH]; hp=[collections.Counter() for _ in TH]; hw=[collections.Counter() for _ in TH]; ww=collections.Counter()
wy=collections.Counter(); wp=collections.Counter(); totw=0; nmo=0
for y in years:
    Y=json.load(open(f'{OUT}/{y}.json')); S=Y['s']; nmo+=len(Y['mo'])
    for i,t in enumerate(S['t']):
        if S['k'][i] not in SPOKEN or not t: continue
        f=fold(t); w=f.count(' ')+1; wy[y]+=w; totw+=w
        p=S['pa'][i] if S['ro'][i]==0 else -1
        if p>=0: wp[p]+=w
        cw=S['sp'][i] if S['ro'][i] in(2,3) and S['sp'][i]>=0 else -1
        if cw>=0: ww[cw]+=w
        for k,r in enumerate(R):
            c=len(r.findall(f))
            if c:
                hy[k][y]+=c
                if p>=0: hp[k][p]+=c
                if cw>=0: hw[k][cw]+=c
parties=[p for p,_ in wp.most_common() if wp[p]>=150000][:14]
meta['themes']=themes.T
meta['ins']={'names':[t[0] for t in TH],'years':years,
  'ty':[[round(hy[k][y]/wy[y]*1e5,1) for y in years] for k in range(len(TH))],
  'tyn':[[hy[k][y] for y in years] for k in range(len(TH))],
  'parties':[PAL[p] for p in parties],
  'tp':[[round(hp[k][p]/wp[p]*1e5,1) for p in parties] for k in range(len(TH))],
  'tpn':[[hp[k][p] for p in parties] for k in range(len(TH))]}
coll=[s for s,_ in ww.most_common() if ww[s]>=60000][:16]
meta['ins']['coll']=[meta['spk'][s][0] for s in coll]
meta['ins']['tw']=[[round(hw[k][s]/ww[s]*1e5,1) for s in coll] for k in range(len(TH))]
meta['ins']['twn']=[[hw[k][s] for s in coll] for k in range(len(TH))]
# opkomende woorden
W=re.compile(r'[a-z][a-z\-]{4,}')
STOP=set('vervolgt appreciatie apprecieren bespreekpunt hartelijk afrondend meent commissiedebat veegronde verhelderende procent burgercommissielid groenlinks-pvda pvda-fractie forum actua'.split())
cy={};wyw={};dm=collections.defaultdict(set)
for y in years:
    Y=json.load(open(f'{OUT}/{y}.json')); S=Y['s']; c=collections.Counter(); n=0
    for i,t in enumerate(S['t']):
        if S['k'][i]!=0: continue
        ws=W.findall(fold(t)); c.update(ws); n+=len(ws)
        if y>='2025':
            for w in set(ws): dm[w].add((y,S['m'][i]))
    cy[y]=c; wyw[y]=n
names=set(w for x in meta['spk'] for w in W.findall(fold(x[0])))
early=[y for y in ['2018','2019','2020','2021','2022'] if y in wyw]; rec=[y for y in ['2025','2026'] if y in wyw]
we=max(1,sum(wyw[y] for y in early)); wr=max(1,sum(wyw[y] for y in rec)); sc=[]
for w in set().union(*[cy[y].keys() for y in rec]):
    r=sum(cy[y][w] for y in rec); e_=sum(cy[y][w] for y in early)
    if r<45 or len(dm[w])<8 or w in names or w in STOP: continue
    s=(r/wr*1e5+0.15)/(e_/we*1e5+0.15)
    if s>=4: sc.append((s,w,r,e_))
sc.sort(reverse=True)
meta['ins']['rise']=[] if OUT!='out' else [[w,r,e_,[round(cy[y][w]/wyw[y]*1e5,2) for y in years]] for s,w,r,e_ in sc[:36]]
meta['tot']={'words':totw,'moties':nmo}
json.dump(meta,open(os.environ.get('RZ_META',f'{OUT}/meta.json'),'w'),ensure_ascii=False)
print('words',totw,'parties',meta['ins']['parties'])
for k,t in enumerate(TH[:3]+TH[15:17]): print(t[0],meta['ins']['ty'][k])
sp=verg=auto=0
for y in years:
    Y=json.load(open(f'{OUT}/{y}.json')); sp+=sum(1 for k in Y['s']['k'] if k in(0,4)); verg+=sum(1 for m in Y['M'] if m[3]==1); auto+=sum(1 for m in Y['M'] if m[3]==2)
if YSEL: meta['years']=[y for y in meta['years'] if y['y'] in YSEL.split(',')]
tzn=sum(len(json.load(open(f'{OUT}/{y}.json'))['tz']) for y in years)
meta['tot'].update({'sp':sp,'verg':verg,'auto':auto,'toez':tzn})
json.dump(meta,open(os.environ.get('RZ_META',f'{OUT}/meta.json'),'w'),ensure_ascii=False)
