import pickle,json,re,collections,zstandard,base64,gzip,os,sys
import subs, motions, toez
from paden import DATA,STAND
import build as B   # reruns build (cheap) and gives REG/person/key etc.
A=B.A; DOC=B.DOC; out=B.out_dates; SPL=B.SPL; PAL=B.PAL; ROLES=B.ROLES; TL=B.TL
def vref(a):
    if not a or not a.get('video'): return ''
    v=a['video']
    return ('c:' if v.startswith('gemeenterotterdam') else 'i:')+v
ZIT={'':0,'ochtend':1,'middag':2,'avond':3,'nacht':4}
bydate=collections.defaultdict(list)
for a in A: bydate[a['date']].append(a)
def main_agenda(date):
    c=[a for a in bydate.get(date,[]) if not re.search(r'hoorzitting|inspreek|tafeltjes|technische|inwerk|jongerendebat|VERVALLEN',a['suffix'],re.I)] or bydate.get(date,[])
    return max(c,key=lambda a:len(a['items'])) if c else None
years=collections.defaultdict(lambda:{'M':[],'D':[],'I':[],'s':{k:[] for k in('m','i','k','sp','pa','ro','pg','d','z','t','v')}})
used=set()
stats=collections.Counter()
for date,(dl,rows) in sorted(out.items()):
    Y=years[date[:4]]
    a=main_agenda(date)
    if a: used.add(a['id'])
    mi=len(Y['M']); Y['M'].append([date,a['id'] if a else None,(a['suffix'] if a else ''),1])
    dmap={}
    for docId,_ in dl:
        d=DOC[docId]; dmap[docId]=len(Y['D']); Y['D'].append([docId,d['agendaId'],d['itemId'],re.sub(r'\s+\d+ [KM]B$','',d['title'])])
    seen=set(); dupprev=False; keep=[]
    for r in rows:
        s=r[0]; kk=(s['pg'],s['kind'],s.get('name',''),s['text'][:160],len(s['text']))
        if len(s['text'])>60:
            dupprev = kk in seen; seen.add(kk)
        if dupprev: stats['dupseg']+=1; continue
        keep.append(r)
    rows=keep
    cur=None; ii=None
    cs=subs.cues(a['video'].replace('/','_')) if a and a['video'] else None
    if cs:
        tms,exs=subs.align([s['text'] for s,_,_,_,_ in rows],cs); stats['aligned']+=sum(exs); stats['alignable']+=len(exs)
    else: tms=[-1]*len(rows)
    Y['M'][mi].append(vref(a))
    for (s,sp,pa,ro,func),tm in zip(rows,tms):
        itk=(s['nr'],s['title'])
        if itk!=cur:
            cur=itk; ii=len(Y['I']); Y['I'].append([mi,s['nr'],s['title'][:400]])
        S=Y['s']
        S['m'].append(mi); S['i'].append(ii); S['k'].append({'sp':0,'doc':1,'pre':2}[s['kind']]); S['sp'].append(sp); S['pa'].append(pa); S['ro'].append(ro)
        S['pg'].append(s['pg'] or 0); S['d'].append(dmap[s['doc']]); S['z'].append(ZIT.get(s['zit'],0)); S['t'].append(s['text']); S['v'].append(tm)
        stats[s['kind']]+=1
# meetings without notulen
import datetime
today=STAND
nm=0
for a in sorted(A,key=lambda a:a['date']):
    if a['id'] in used or a['date']>today or 'VERVALLEN' in a['label']: continue
    if a['date'] in out: continue   # side meeting on a notulen day -> skip
    ent=TL.get(a['id'],[])
    if not a['items']: continue
    Y=years[a['date'][:4]]; y=int(a['date'][:4])
    mi=len(Y['M']); Y['M'].append([a['date'],a['id'],a['suffix'],0,vref(a)]); nm+=1
    imap={}
    for k,it in enumerate(a['items']):
        imap[k]=len(Y['I']); Y['I'].append([mi,it['nr'].rstrip('.'),it['title'][:400]])
    cs=subs.cues(a['video'].replace('/','_')) if a['video'] else None
    def who(o):
        if o['sur']:
            k=B.key(o['sur']); pr=B.person(k,y)
            disp=pr[0] if pr else o['sur']; sort=re.sub(r'^(VAN DER|VAN DEN|VAN DE|VAN|DE|DEN|EL|TER|LA) ','',k)
        else:
            g=o.get('generic','')
            disp='Voorzitter' if o['role']=='voorzitter' else (g[:1].upper()+g[1:] if g else 'Onbekende spreker'); sort=disp.upper()
        if o.get('func') and not o['sur']: disp+=' ('+o['func'].lower()+')'
        return B.spk(disp,sort),B.par(o['party']),ROLES.index(o['role'])
    def secs(t): hh,mm_,ss=map(int,t.split(':')); return hh*3600+mm_*60+ss
    S=Y['s']
    def add(ii,k,sp,pa,ro,sec,text):
        S['m'].append(mi); S['i'].append(ii); S['k'].append(k); S['sp'].append(sp); S['pa'].append(pa); S['ro'].append(ro)
        S['pg'].append(sec); S['d'].append(-1); S['z'].append(0); S['t'].append(text); S['v'].append(sec)
    turns=[]; last=None
    for o in sorted(ent,key=lambda o:secs(o['t'])):
        w=who(o); keyt=(o['item'],w[0])
        if keyt==last: continue
        last=keyt; turns.append((secs(o['t']),o['item'],w))
    if cs:
        Y['M'][mi][3]=2; stats['gapfilled']+=1
        import bisect
        ct=[c[0] for c in cs]
        if turns:
            segs=[]
            for n,(st,it,w) in enumerate(turns):
                en=turns[n+1][0] if n+1<len(turns) else 10**9
                lo=bisect.bisect_left(ct,st-2 if n else -1); hi=bisect.bisect_left(ct,en-2)
                tx=' '.join(c[1] for c in cs[lo:hi]).strip()
                if tx: segs.append((it,st,w,tx))
            for it,st,w,tx in sorted(segs,key=lambda x:(x[0],x[1])): add(imap[it],4,w[0],w[1],w[2],st,tx); stats['sub']+=1
        else:
            ii=len(Y['I']); Y['I'].append([mi,'','Uitzending (geen sprekerstijdlijn)'])
            buf=[];st=None
            for t,x in cs:
                if st is None: st=t
                buf.append(x)
                if t-st>=75 and re.search(r'[.?!]$',x) or t-st>150:
                    add(ii,4,-1,-1,5,st,' '.join(buf)); stats['sub']+=1; buf=[];st=None
            if buf: add(ii,4,-1,-1,5,st,' '.join(buf))
    else:
        for st,it,w in sorted(turns,key=lambda x:(x[1],x[0])): add(imap[it],3,w[0],w[1],w[2],st,''); stats['tl']+=1
print('meetings without notulen:',nm,stats)
os.makedirs('out',exist_ok=True)
meta={'spk':SPL,'par':PAL,'roles':ROLES,'years':[],'built':STAND,'src':'https://gemeenteraad.rotterdam.nl'}
cctx=zstandard.ZstdCompressor(level=22)
tot=0
for y in sorted(years):
    Y=years[y]
    S=Y['s']; mo=[]; seen=set()
    for i,t in enumerate(S['t']):
        if S['k'][i] not in(0,1) or (S['k'][i]==0 and S['ro'][i]!=1): continue
        if 'aangenomen' not in t and 'verworpen' not in t and 'aanvaard' not in t: continue
        for m in motions.find(t):
            if m['res'] not in('aangenomen','verworpen'): continue
            kk=(S['m'][i],m['typ'],m['nr'],m['title'][:25].lower(),m['res'])
            if kk in seen: continue
            seen.add(kk); mo.append([i,m['typ'][0],m['nr'],m['title'],1 if m['res']=='aangenomen' else 0,m['voor'],m['tegen'],m['side'][:1],m['fr']])
    Y['mo']=mo; stats['moties']+=len(mo)
    tz=[]
    for i,t in enumerate(S['t']):
        if S['k'][i] in(0,4) and S['ro'][i] in(2,3) and S['sp'][i]>=0:
            hard=toez.find(t) if 'toe' in t else []
            for a,b in hard: tz.append([i,a,b,0])
            for a,b in toez.find(t,toez.P2):
                if not any(a<hb and b>ha for ha,hb in hard): tz.append([i,a,b,1])
    Y['tz']=tz; stats['toez']+=len(tz)
    import glob
    src={}
    # id -> (datum, agendapunt); de oorspronkelijke invoerbestanden zijn niet bewaard, data/sum/index.json is daaruit afgeleid
    for k,v in json.load(open(f'{DATA}/sum/index.json')).items(): src[int(k)]=tuple(v)
    summ={}
    for f in sorted(glob.glob(f'{DATA}/sum/out_*.json')):
        for d in json.load(open(f)):
            if d['id'] in src: summ.setdefault(src[d['id']],d)
    sm={}
    if y=='2026':
        firstseg={}
        for i,it in enumerate(Y['s']['i']): firstseg.setdefault(it,i)
        wc=collections.Counter()
        for i,it in enumerate(Y['s']['i']): wc[it]+=len(Y['s']['t'][i])
        best={}
        for it,I_ in enumerate(Y['I']):
            k=(Y['M'][I_[0]][0],(I_[1]+' '+I_[2]).strip())
            if k in summ and wc[it]>wc.get(best.get(k,-1),0): best[k]=it
        for k,it in best.items():
            d=summ[k]; sm[it]=[d['kern'],[[p['wie'],p['punt']] for p in d.get('standpunten',[])],d.get('uitkomst','')]
        stats['samenvattingen']+=len(sm)
    Y['sm']=sm
    raw=json.dumps(Y,ensure_ascii=False,separators=(',',':')).encode('utf8')
    z=cctx.compress(raw); g=gzip.compress(raw,9)
    open(f'out/{y}.zst','wb').write(z)
    json.dump(Y,open(f'out/{y}.json','w'),ensure_ascii=False)
    nN=sum(1 for m in Y['M'] if m[3]==1); 
    meta['years'].append({'y':y,'raw':len(raw),'z':len(z),'meet':len(Y['M']),'notulen':nN,'seg':len(Y['s']['t'])})
    tot+=len(z)
    print(y,len(raw)//1000,'kB raw',len(z)//1000,'zst',len(g)//1000,'gz','meet',len(Y['M']),'notulen',nN,'segs',len(Y['s']['t']))
json.dump(meta,open('out/meta.json','w'),ensure_ascii=False)
print(stats)
print('total zst MB',tot/1e6,'b64 MB',tot*4/3/1e6, 'speakers',len(SPL))
