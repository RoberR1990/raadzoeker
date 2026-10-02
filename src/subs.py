import json,re,unicodedata,collections,bisect
R=json.load(open('subs.json'))
def fold(s): return ''.join(c for c in unicodedata.normalize('NFD',s.lower()) if unicodedata.category(c)!='Mn')
W=re.compile(r'[a-z0-9]+')
def cues(vid):
    r=R.get(vid)
    if not r or r['st']!='ok' or r['n']<=20: return None
    out=[]; last=None
    for l in r['c'].split('\n'):
        t,_,x=l.partition('\t')
        if x==last and 'vergadering begint' in x: continue
        last=x; out.append((int(t),x))
    return out
def align(texts,cs):
    """texts: list of str (speech order). returns list of seconds or -1, and exact flags"""
    words=[];wt=[]
    for t,x in cs:
        for w in W.findall(fold(x)): words.append(w); wt.append(t)
    idx=collections.defaultdict(list)
    for i in range(len(words)-2): idx[(words[i],words[i+1],words[i+2])].append(i)
    cand=[]
    for si,tx in enumerate(texts):
        ws=W.findall(fold(tx[:600]))[:70]
        if len(ws)<6: cand.append(None); continue
        votes=collections.Counter()
        for k in range(len(ws)-2):
            ps=idx.get((ws[k],ws[k+1],ws[k+2]))
            if ps and len(ps)<=4:
                for p in ps: votes[(p-k)//12]+=1
        best=None
        if votes:
            b,c=votes.most_common(1)[0]
            c+=votes.get(b-1,0)+votes.get(b+1,0)
            if c>=max(3,min(8,len(ws)//6)): best=b*12
        cand.append(best)
    # longest increasing subsequence over candidates
    pts=[(i,c) for i,c in enumerate(cand) if c is not None]
    tails=[];tl_idx=[];prev=[-1]*len(pts)
    for k,(i,c) in enumerate(pts):
        j=bisect.bisect_right(tails,c)
        if j==len(tails): tails.append(c); tl_idx.append(k)
        else: tails[j]=c; tl_idx[j]=k
        prev[k]=tl_idx[j-1] if j>0 else -1
    keep=set(); k=tl_idx[-1] if tl_idx else -1
    while k>=0: keep.add(pts[k][0]); k=prev[k]
    out=[];ex=[];lastt=-1
    for i,c in enumerate(cand):
        if i in keep:
            p=max(0,min(len(wt)-1,c)); lastt=wt[p]; out.append(lastt); ex.append(1)
        else: out.append(lastt); ex.append(0)
    return out,ex
