import json,re,collections,gzip,bisect,sys,os,zstandard,io,contextlib
sys.path.insert(0,'.')
with contextlib.redirect_stdout(io.StringIO()):
    import build as B
import toez
U='/mnt/user-data/uploads/Downloads Chrome/'
M=json.load(open('cmeta.json'))
R={}
for f in ['raadzoeker-commissies-subs-c.json.gz','raadzoeker-commissies-subs-i.json.gz']:
    R.update(json.load(gzip.open(U+f,'rt',encoding='utf8')))
CAT={c['id']:re.sub(r'^zzz ','',c['name']) for c in M['cats']}
MND={m:i+1 for i,m in enumerate('januari februari maart april mei juni juli augustus september oktober november december'.split())}
ROLES=B.ROLES
SPK={};SPL=[];PAR={};PAL=[]
def spk(d,s):
    if d not in SPK: SPK[d]=len(SPL); SPL.append([d,s])
    return SPK[d]
def par(p):
    if p is None: return -1
    if p not in PAR: PAR[p]=len(PAL); PAL.append(p)
    return PAR[p]
def cues(vid):
    r=R.get(vid)
    if not r or r.get('st')!='ok' or r['n']<=20: return None
    out=[];last=None
    for l in r['c'].split('\n'):
        t,_,x=l.partition('\t')
        if x==last and 'vergadering begint' in x: continue
        last=x; out.append((int(t),x))
    return out
def secs(t): hh,mm,ss=map(int,t.split(':')); return hh*3600+mm*60+ss
years=collections.defaultdict(lambda:{'M':[],'D':[],'I':[],'mo':[],'tz':[],'sm':{},'s':{k:[] for k in('m','i','k','sp','pa','ro','pg','d','z','t','v')}})
st=collections.Counter(); seenv=set()
for a in sorted(M['ag'],key=lambda a:a['label']):
    d=M['det'].get(a['id']) or {}
    if not d.get('vid'): continue
    key=d['vid'].replace('/','_') if d['vt']=='Cwc' else d['vid']
    if key in seenv: continue
    cs=cues(key)
    if not cs: st['geen ondertiteling']+=1; continue
    mm=re.search(r'(\d{1,2}) (\w+) (\d{4})',a['label'])
    if not mm or mm.group(2).lower() not in MND: st['geen datum']+=1; continue
    seenv.add(key)
    date='%s-%02d-%02d'%(mm.group(3),MND[mm.group(2).lower()],int(mm.group(1))); y=int(date[:4])
    Y=years[date[:4]]; S=Y['s']; mi=len(Y['M'])
    Y['M'].append([date,a['id'],CAT.get(a['cat'],''),2,('c:' if d['vt']=='Cwc' else 'i:')+d['vid']])
    imap={}
    for k,it in enumerate(d['items']): imap[k]=len(Y['I']); Y['I'].append([mi,it['nr'].strip().rstrip('.'),it['title'][:400]])
    turns=[];last=None
    ent=[]
    for k,it in enumerate(d['items']):
        for t in it['sp']:
            o=B.parse_tl(t)
            if o: o['item']=k; ent.append(o)
    for o in sorted(ent,key=lambda o:secs(o['t'])):
        if o['sur']:
            kk=B.key(o['sur']); pr=B.person(kk,y)
            disp=pr[0] if pr else ((o['first']+' ' if o.get('first') else (o['init'].strip()+' ' if o.get('init') else ''))+o['sur'])
            sort=re.sub(r'^(VAN DER|VAN DEN|VAN DE|VAN|DE|DEN|EL|TER|LA) ','',kk)
        else:
            g=o.get('generic',''); disp='Voorzitter' if o['role']=='voorzitter' else (g[:1].upper()+g[1:] if g else 'Onbekende spreker'); sort=disp.upper()
        w=(spk(disp,sort),par(o['party']),ROLES.index(o['role'])); kt=(o['item'],w[0])
        if kt==last: continue
        last=kt; turns.append((secs(o['t']),o['item'],w))
    def add(ii,sp,pa,ro,sec,text):
        S['m'].append(mi);S['i'].append(ii);S['k'].append(4);S['sp'].append(sp);S['pa'].append(pa);S['ro'].append(ro);S['pg'].append(sec);S['d'].append(-1);S['z'].append(0);S['t'].append(text);S['v'].append(sec); st['seg']+=1
    ct=[c[0] for c in cs]
    if turns:
        segs=[]
        for n,(s0,it,w) in enumerate(turns):
            en=turns[n+1][0] if n+1<len(turns) else 10**9
            lo=bisect.bisect_left(ct,s0-2 if n else -1); hi=bisect.bisect_left(ct,en-2)
            tx=' '.join(c[1] for c in cs[lo:hi]).strip()
            if tx: segs.append((it,s0,w,tx))
        for it,s0,w,tx in sorted(segs,key=lambda x:(x[0],x[1])): add(imap[it],w[0],w[1],w[2],s0,tx)
        st['met tijdlijn']+=1
    else:
        ii=len(Y['I']); Y['I'].append([mi,'','Uitzending (geen sprekerstijdlijn)'])
        buf=[];s0=None
        for t,x in cs:
            if s0 is None: s0=t
            buf.append(x)
            if (t-s0>=75 and re.search(r'[.?!]$',x)) or t-s0>150: add(ii,-1,-1,5,s0,' '.join(buf)); buf=[];s0=None
        if buf: add(ii,-1,-1,5,s0,' '.join(buf))
        st['zonder tijdlijn']+=1
    st['verg']+=1
print(st)
cctx=zstandard.ZstdCompressor(level=22)
os.makedirs('outc',exist_ok=True)
meta={'spk':SPL,'par':PAL,'roles':ROLES,'years':[],'built':'2026-10-02','src':'https://gemeenteraad.rotterdam.nl','kind':'c','cats':sorted({m[2] for Y in years.values() for m in Y['M']})}
for y in sorted(years):
    Y=years[y];S=Y['s'];tz=[]
    for i,t in enumerate(S['t']):
        if S['ro'][i] in(2,3) and S['sp'][i]>=0:
            hard=toez.find(t) if 'toe' in t else []
            for a_,b_ in hard: tz.append([i,a_,b_,0])
            for a_,b_ in toez.find(t,toez.P2):
                if not any(a_<hb and b_>ha for ha,hb in hard): tz.append([i,a_,b_,1])
    Y['tz']=tz
    raw=json.dumps(Y,ensure_ascii=False,separators=(',',':')).encode('utf8'); z=cctx.compress(raw)
    open(f'outc/{y}.zst','wb').write(z); json.dump(Y,open(f'outc/{y}.json','w'),ensure_ascii=False)
    meta['years'].append({'y':y,'raw':len(raw),'z':len(z),'meet':len(Y['M']),'notulen':0,'seg':len(S['t'])})
    print(y,len(raw)//1000000,'MB raw',len(z)/1e6,'zst','verg',len(Y['M']),'seg',len(S['t']),'toez',len(tz))
json.dump(meta,open('outc/meta.json','w'),ensure_ascii=False)
print('speakers',len(SPL),'parties',PAL)
