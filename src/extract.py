import pymupdf, json, os, re, sys
from multiprocessing import Pool
RAW='/home/claude/raw'
def page_lines(p):
    spans=[]; pageno=None
    for b in p.get_text('dict')['blocks']:
        if b['type']!=0: continue
        for l in b['lines']:
            d=l.get('dir',(1,0))
            if abs(d[0]-1)>0.01: continue
            for s in l['spans']:
                t=s['text']
                if not t.strip(): 
                    # keep blank marker for paragraph gaps
                    continue
                x0,y0,x1,y1=s['bbox']
                spans.append([x0,y0,x1,y1,t,1 if 'Bold' in s['font'] and 'Bolder' not in s['font'] else 0,1 if 'Italic' in s['font'] else 0,s['size']])
    H=p.rect.height
    body=[]; foot=[]
    for s in spans:
        (foot if (s[1]>H*0.893 or s[3]<40 or (s[1]>H*0.84 and (s[7]<=8.6 or s[4].strip() in('Notulen','pagina')))) else body).append(s)
    ft=' '.join(s[4].strip() for s in sorted(foot,key=lambda s:(round(s[1]),s[0])))
    m=re.search(r'pagina\s*(\d+)',ft)
    if m: pageno=int(m.group(1))
    # group spans into visual lines by y
    body.sort(key=lambda s:(s[1],s[0]))
    mid=p.rect.width/2
    cross=[s for s in body if s[0]<mid-12 and s[2]>mid+12]
    right=[s for s in body if mid-5<=s[0]<=mid+45]
    left=[s for s in body if s[2]<=mid+2]
    twocol = len(right)>=3 and len(left)>=3 and len(cross)<=0.2*len(body)
    def col(s):
        if not twocol: return 0
        if s[0]<mid-12 and s[2]>mid+12: return -1
        return 0 if s[0]<mid-5 else 1
    fy=sorted(s[1] for s in body if col(s)==-1)
    def band(s):
        c=col(s)
        if c==-1: return sum(1 for y in fy if y<=s[1]+0.01)
        return sum(1 for y in fy if y<s[1]-3)
    items=sorted(body,key=lambda s:(band(s),col(s),round(s[1]/3),s[0]))
    lines=[]
    for s in items:
        key=(band(s),col(s))
        if lines and lines[-1]['k']==key and abs(lines[-1]['y']-s[1])<4:
            L=lines[-1]
            gap=s[0]-L['x1']
            L['t']+=('\t' if gap>9 else ('' if (L['t'].endswith(' ') or s[4].startswith(' ') or gap<0.8) else ' '))+s[4]
            L['x1']=max(L['x1'],s[2]); L['b']|=s[5]; L['i']&=s[6]
        else:
            lines.append({'k':key,'x0':s[0],'y':s[1],'x1':s[2],'h':s[3]-s[1],'t':s[4],'b':s[5],'i':s[6],'sz':s[7]})
    out=[[round(L['x0'],1),round(L['y'],1),round(L['x1'],1),L['t'].strip(' '),L['b'],L['i'],L['k'][1],round(L['sz'],1)] for L in lines]
    return {'n':pageno,'two':twocol,'lines':out,'foot':ft}
def do(docId):
    out=f'lines/{docId}.json'
    if os.path.exists(out): return docId
    d=pymupdf.open(f'{RAW}/doc/{docId}.pdf')
    pages=[page_lines(p) for p in d]
    json.dump(pages,open(out,'w'),ensure_ascii=False)
    return docId
if __name__=='__main__':
    os.makedirs('lines',exist_ok=True)
    h=json.load(open(f'{RAW}/header.json'))
    ids=[d['docId'] for d in h['docs']]
    with Pool(8) as pool:
        for i,_ in enumerate(pool.imap_unordered(do,ids)): pass
    print('done',len(ids))
