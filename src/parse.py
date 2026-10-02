import json,re,collections,statistics,sys
from paden import RAW
h=json.load(open(f'{RAW}/header.json'))
A=json.load(open('agendas.json'))
MND={m:i+1 for i,m in enumerate('januari februari maart april mei juni juli augustus september oktober november december'.split())}
UP="A-ZÀ-ÖØ-ÞŞİĞŁŒ"
SP=re.compile(r"^(De heer|De her|De hee|Mevrouw|Mijnheer|Wethouder|Burgemeester|De|DE)?\s*((?:[Dd]e |[Vv]an [Dd]e[rn]? |[Vv]an |[Ee]l |[Tt]er )?["+UP+r"]["+UP+r"'’\-]+(?: ["+UP+r"'’\-]{2,})*)\s*[,|I]?\s*((?:\([^)]{1,45}\)?\.?\s*){0,2})((?:wethouder|burgemeester)\))?\s*([.:])?\s*(.*)$")
HD=re.compile(r'^(\d{1,3}[a-z]?(?:\.\d{1,3}){0,2})\.?[ \t]+(\S.*)$')
SIT=re.compile(r'^Notulen (?:van de )?(?:openbare |buitengewone |besloten )*raadsvergadering(?:en)? (?:van |op )?(?:\w+dag )?(.{4,70}?\d{4})\s*(?:\(\s*(ochtend|middag|avond|nacht)[\w-]*\s*([^)]*)\))?',re.I)
FT=re.compile(r'(\d{1,2}) (\w+) (\d{4})')
MRX='|'.join(MND)
DL=re.compile(r'(?<!\d)((?:\d{1,2}\s*(?:,|en)\s*)*\d{1,2}) ('+MRX+r')(?: (\d{4}))?',re.I)
def datelist(t):
    out=[]; ms=list(DL.finditer(t)); 
    yrs=[m.group(3) for m in ms if m.group(3)]
    for m in ms:
        y=m.group(3) or (yrs[-1] if yrs else None)
        if not y: continue
        for d in re.findall(r'\d{1,2}',m.group(1)):
            if 1<=int(d)<=31: out.append('%s-%02d-%02d'%(y,MND[m.group(2).lower()],int(d)))
    return out
def iso(d,m,y):
    m=MND.get(m.lower())
    return '%s-%02d-%02d'%(y,m,int(d)) if m else None
def is_speaker(t,bold):
    m=SP.match(t)
    if not m: return None
    pfx,name,par,extra,punct,rest=m.groups()
    core=re.sub(r'^(?:[Dd]e |[Vv]an [Dd]e[rn]? |[Vv]an |[Ee]l |[Tt]er )','',name)
    if len(re.sub(r"[^"+UP+"]",'',core))<3: return None
    if not par and not extra and not punct: return None
    if pfx is None:
        if not re.match(r'^(DE )?V\w*O+R?Z\w*T+ERS?$',name): return None
    elif pfx in('De','DE'):
        if len(core)<5 and not bold: return None
        if name.startswith(('de ','van ')): return None
    pars=re.findall(r'\(([^)]*)\)?',par)
    pars=[re.split(r'(?<=[a-z0-9+])\.\s+(?=[A-Z])',p.strip(' .('))[0].strip() for p in pars if p.strip(' .(')]
    if extra: pars.append(extra.strip(')'))
    return (pfx or 'De',name,pars,rest)
def parse_doc(d):
    pages=json.load(open(f"lines/{d['docId']}.json"))
    segs=[]; cur=None; date=None; zit=''; item=('',''); 
    state={'hd':None}
    td=datelist(d['title'])
    def new(kind,pi,p,**kw):
        nonlocal cur
        cur={'kind':kind,'date':date,'zit':zit,'nr':item[0],'title':item[1],'pg':p['n'],'pp':pi+1,'doc':d['docId'],'paras':[[]],**kw}
        segs.append(cur)
    for pi,p in enumerate(pages):
        L=p['lines']
        if not L: continue
        fds=datelist(p['foot'] or '')
        if fds and date not in fds and not (L and SIT.match(L[0][3]+' '+(L[1][3] if len(L)>1 else ''))):
            if len(fds)==1 or date is None: date=fds[0]
        prev=None; hd_open=False
        dys=[L[i+1][1]-L[i][1] for i in range(len(L)-1) if L[i+1][6]==L[i][6] and 5<L[i+1][1]-L[i][1]<20]
        pitch=statistics.median(dys) if dys else 12.6
        i=0
        while i<len(L):
            x0,y,x1,t,b,it,col,sz=L[i]
            t=t.replace('­','').replace('\xa0',' ')
            gap = prev is None or col!=prev[6] or (y-prev[1])>pitch*1.45 or y<prev[1]
            newcol = prev is None or col!=prev[6] or y<prev[1]
            # sitting header
            if t.startswith('Notulen') and re.match(r'^Notulen (?:van de )?(?:openbare |buitengewone |besloten )*raadsvergadering(?:en)? ',t+' '):
                joined=re.sub(r'\s+',' ',' '.join(x[3] for x in L[i:i+6]))
                mm=re.search(r'\)|Voor de agenda|Voorzitter\s*:|Tegenwoordig|Aanwezig',joined)
                hdr=joined[:mm.end()] if (mm and mm.group(0)==')') else (joined[:mm.start()] if mm else joined[:160])
                look=' '.join(x[3] for x in L[i:i+18])
                ms=list(DL.finditer(hdr)); alld=datelist(hdr)
                m=ms[0] if ms else None
                if m and alld and re.search(r'Voorzitter\s*:|Voor de agenda|Tegenwoordig|Aanwezig',look):
                    yr=alld[0][:4]; pick=None; allmain=[]
                    for cl in re.split(r'(?=Notulen )',hdr):
                        cms=list(DL.finditer(cl))
                        if not cms: continue
                        end=cms[0].end()
                        for k in range(1,len(cms)):
                            if re.match(r'^\s*(en|,)\s*$',cl[end:cms[k].start()]): end=cms[k].end()
                            else: break
                        maintext=cl[cms[0].start():end]
                        main=datelist(maintext+('' if re.search(r'\d{4}',maintext) else ' '+yr)); allmain+=main
                        spec=datelist(cl[end:]+' 1 januari '+yr)[:-1]
                        if spec: pick=(2,spec[-1])
                        elif len(main)==1 and (pick is None or pick[0]<2): pick=(1,main[0])
                    if pick: date=pick[1]
                    elif date not in allmain: date=allmain[0]
                    zm=re.search(r'(ochtend|middag|avond|nacht)',hdr,re.I)
                    zit=zm.group(1).lower() if zm else ''
                    class _M: 
                        def group(self,n): return hdr
                    m=_M()
                    item=('','')
                    new('pre',pi,p)
                    # skip header lines (those until text consumed)
                    consumed=len(re.sub(r'\s+','',m.group(0)))
                    acc=0
                    while i<len(L) and acc<consumed:
                        acc+=len(re.sub(r'\s+','',L[i][3])); prev=L[i]; i+=1
                    hd_open=False
                    continue
            if t in('Notulen raadsvergadering',) : prev=L[i]; i+=1; continue
            t1=t.replace('\t',' ')
            sp=is_speaker(t1,b)
            two=False
            if i+1<len(L) and L[i+1][6]==col and re.match(r"^(De heer|De her|Mevrouw|Mijnheer|De|Wethouder|Burgemeester) (?:[Dd]e |[Vv]an )?["+UP+"]{2}",t1):
                head=t1[:70]
                if (not sp) or head.count('(')>head.count(')') :
                    j=join([t1,L[i+1][3].replace('\t',' ')])
                    sp2=is_speaker(j,b)
                    if sp2 and j[:90].count('(')<=j[:90].count(')')+ (0 if sp else 1): sp=sp2; two=True
            if sp:
                if two: prev=L[i]; i+=1
                new('sp',pi,p,pfx=sp[0],name=sp[1],pars=sp[2])
                if sp[3]: cur['paras'][-1].append(sp[3])
                hd_open=False; prev=L[i]; i+=1; continue
            m=HD.match(t)
            if m and (it or '\t' in t) and (gap) and re.match(r"[A-ZÀ-Þ‘'\"(]",m.group(2).strip()):
                item=(m.group(1),m.group(2).strip().replace('\t',' '))
                state['hd']={'it':it,'x':x0}
                hd_open=True
                new('hd',pi,p); cur['nr'],cur['title']=item
                prev=L[i]; i+=1
                # continuation lines
                while i<len(L):
                    n=L[i]
                    cont = n[6]==col and 0<(n[1]-prev[1])<pitch*1.45 and not is_speaker(n[3].replace('\t',' '),n[4]) and (n[5] if it else True)
                    # heading may continue in next column / page? ignore
                    if not cont: break
                    item=(item[0],item[1]+' '+n[3].strip()); prev=n; i+=1
                cur['title']=item[1]
                continue
            if cur is None: new('pre',pi,p)
            if cur['kind']=='hd':
                new('nar',pi,p)   # narrative text directly after heading without speaker
            tt=t.replace('\t',' ')
            if gap and not newcol and cur['paras'][-1]: cur['paras'].append([])
            cur['paras'][-1].append(tt)
            prev=L[i]; i+=1
    return segs
def join(lines):
    out=''
    for l in lines:
        l=l.strip()
        if not l: continue
        if not out: out=l
        elif out.endswith('-') and len(out)>1 and out[-2].isalpha() and not re.match(r'(en|of)\b',l): out+=l
        else: out+=' '+l
    return re.sub(r'\s+',' ',out)
if __name__=='__main__':
    allsegs={}
    for d in h['docs']:
        segs=parse_doc(d)
        for s in segs:
            s['text']='\n'.join(x for x in (join(p) for p in s.pop('paras')) if x)
        allsegs[d['docId']]=segs
    json.dump(allsegs,open('segs.json','w'),ensure_ascii=False)
    c=collections.Counter(s['kind'] for v in allsegs.values() for s in v)
    print(c, sum(len(s['text']) for v in allsegs.values() for s in v)/1e6)
