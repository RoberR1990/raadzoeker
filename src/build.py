import json,re,collections,difflib,unicodedata,os,sys
from paden import RAW
h=json.load(open(f'{RAW}/header.json'))
A=json.load(open('agendas.json'))
S=json.load(open('segs.json'))
DOC={d['docId']:d for d in h['docs']}
MND={m:i+1 for i,m in enumerate('januari februari maart april mei juni juli augustus september oktober november december'.split())}
def fold(s): return ''.join(c for c in unicodedata.normalize('NFD',s) if unicodedata.category(c)!='Mn')
def key(s): return re.sub(r'[^A-Z ]','',fold(s).upper().replace('-',' ')).strip()
TV={'van','de','der','den','ter','te','el','la','da','het',"'t",'op','in'}
def tcase(name,first=True):
    out=[]
    for i,w in enumerate(name.lower().split()):
        if w in TV and not(first and i==0): out.append(w)
        else: out.append('-'.join(p[:1].upper()+p[1:] if (p not in TV or j==0) else p for j,p in enumerate(w.split('-'))))
    return ' '.join(out)
PARTY={'lr':'Leefbaar Rotterdam','leefbaar rotterdam':'Leefbaar Rotterdam','l':'Leefbaar Rotterdam','vvd':'VVD','gl':'GroenLinks','groenlinks':'GroenLinks','pvda':'PvdA','pdva':'PvdA','d66':'D66','d6e':'D66','denk':'DENK','sp':'SP',
 'pvdd':'Partij voor de Dieren','partij voor de dieren':'Partij voor de Dieren','cda':'CDA','50plus':'50PLUS','50+':'50PLUS','50-plus':'50PLUS','50lus':'50PLUS','nida':'NIDA','volt':'Volt',
 'cu':'ChristenUnie-SGP','cu-sgp':'ChristenUnie-SGP','vu-sgp':'ChristenUnie-SGP','christenunie-sgp':'ChristenUnie-SGP','christenunie':'ChristenUnie-SGP','pvv':'PVV','bij1':'BIJ1','bij 1':'BIJ1','pro':'PRO','fvd':'Forum voor Democratie','forum voor democratie':'Forum voor Democratie',
 'fractie-verveen':'Fractie Verveen','gdj':'Groep De Jong','groep de jong':'Groep De Jong','gv':'Groep Verkoelen','groep verkoelen':'Groep Verkoelen','gvdv':'Groep Van der Velden','groep van der velden':'Groep Van der Velden','fractie-peksert':'Fractie Peksert','gl-pvda':'GroenLinks-PvdA','groenlinks-pvda':'GroenLinks-PvdA'}
ROLEW=['Plaatsvervangende voorzitter','Plaatsvervangend voorzitter','Plaatsvervangend griffier','Commissievoorzitter','Burgercommissielid','Kandidaat-wethouder','Nestor van de gemeenteraad','Fractievoorzitter','Informateur','Inspreker','Raadslid','Voorzitter','Wethouder','Burgemeester','Griffier','Burgerlid','COR-lid']
def rolecode(r):
    r=r.lower()
    if 'voorzitter' in r and 'commissie' not in r and 'fractie' not in r: return 'voorzitter'
    if 'wethouder' in r and 'kandidaat' not in r: return 'wethouder'
    if 'burgemeester' in r and 'loco' not in r: return 'burgemeester'
    if 'locoburgemeester' in r: return 'wethouder'
    if 'griffier' in r: return 'griffier'
    if 'raadslid' in r: return 'raadslid'
    return 'overig'
def parse_tl(t):
    m=re.match(r'^(\d\d:\d\d:\d\d) - (\d\d:\d\d:\d\d)? ?- (.*)$',t)
    if not m: return None
    st,en,r=m.groups(); r=r.strip(' .')
    o={'t':st,'first':None,'init':None,'sur':None,'role':'overig','party':None,'raw':r}
    m=re.match(r'^([^,()]+), ((?:[A-ZÀ-Þ]\.? ?)+)([a-z\' ]*)\((.*)\)$',r)
    if m:
        o['sur']=(m.group(3).strip()+' '+m.group(1).strip()).strip(); o['init']=m.group(2).strip(); x=m.group(4)
        if x.lower() in PARTY: o['party']=PARTY[x.lower()]; o['role']='raadslid'
        else: o['role']=rolecode(x)
        return o
    m=re.match(r'^((?:[A-ZÀ-Þ]\.)+) ?\(([^)]+)\) (.+)$',r)
    if m:
        o['init'],o['first'],rest=m.groups()
        for rw in ROLEW:
            mm=re.search(r' '+rw+r'\b(.*)$',rest)
            if mm:
                m2=re.search(r' (?:Inspreker|Raadslid|Voorzitter)\b',rest[:mm.start()])
                if m2: rest=rest[:m2.start()]+rest[mm.start():]; mm=re.search(r' '+rw+r'\b(.*)$',rest)
                o['sur']=rest[:mm.start()].strip(); o['role']=rolecode(rw); p=mm.group(1).strip()
                if rw in('Burgercommissielid','Raadslid','Fractievoorzitter') and p: o['party']=PARTY.get(p.lower(),p)
                if rw not in('Raadslid',) and o['role']=='overig': o['func']=rw
                return o
        for pn in sorted(set(PARTY.values()),key=len,reverse=True):
            if rest.endswith(' '+pn): o['sur']=rest[:-len(pn)-1].strip(); o['party']=pn; o['role']='raadslid'; return o
        mm=re.match(r'^(.+?) \(([^)]*)\)?$',rest)
        if mm:
            o['sur']=mm.group(1); x=mm.group(2)
            if x.lower() in PARTY: o['party']=PARTY[x.lower()]; o['role']='raadslid'
            else: o['role']=rolecode(x)
        else: o['sur']=rest
        return o
    m=re.match(r'^((?:[A-ZÀ-Þ]\.?)+) (.+?)(?: \(([^)]*)\)?)?$',r)
    if m and '.' in m.group(1):
        o['init']=m.group(1); o['sur']=m.group(2); x=m.group(3)
        if x:
            if x.lower() in PARTY: o['party']=PARTY[x.lower()]; o['role']='raadslid'
            else: o['role']=rolecode(x)
        return o
    o['role']=rolecode(r); o['generic']=r
    return o
# ---------- registry from timelines
REG=collections.defaultdict(lambda: collections.defaultdict(lambda:{'years':collections.Counter(),'first':collections.Counter(),'init':collections.Counter(),'party':collections.Counter(),'role':collections.Counter()}))
TL={}
for a in A:
    y=int(a['date'][:4]); ent=[]
    for ii,it in enumerate(a['items']):
        for t,off in it['sp']:
            o=parse_tl(t)
            if not o: continue
            o['item']=ii; ent.append(o)
            if o['sur']:
                k=key(o['sur'])
                pid=(o['init'] or '').replace(' ','').replace('.','')[:1]  # first initial separates namesakes
                e=REG[k][pid]; e['years'][y]+=1
                if o['first']: e['first'][o['first']]+=1
                if o['init']: e['init'][o['init']]+=1
                if o['party']: e['party'][(y,o['party'])]+=1
                e['role'][(y,o['role'])]+=1; e.setdefault('sur',collections.Counter())[o['sur']]+=1
    TL[a['id']]=ent
def person(k,year,want_role=None):
    """return (display, sortkey, pid) for surname key k in given year"""
    if k not in REG: return None
    cands=REG[k]
    best=min(cands.items(),key=lambda kv:(min(abs(year-y) for y in kv[1]['years']),-sum(kv[1]['years'].values())))
    pid,e=best
    sur=e['sur'].most_common(1)[0][0]
    sur_l=' '.join(w if w.lower() in TV else w for w in sur.split())
    if e['first']: disp=e['first'].most_common(1)[0][0]+' '+sur_l
    elif e['init']: disp=e['init'].most_common(1)[0][0].strip()+' '+sur_l
    else: disp=sur_l
    return disp,pid,e
# ---------- collect segments, fix dates, split doc blocks
from parse import datelist as title_dates
MOT=re.compile(r"^(?:Motie|Amendement|Subamendement)\s+\S{1,6}[.,:]?\s")
GEM=re.compile(r"^\W{0,3}De (?:gemeente)?raad van (?:de gemeente )?Rotterdam,?\s+(?:in (?:openbare )?vergadering )?bijeen",re.I)
CON=re.compile(r"^\W{0,3}(?:constaterende|overwegende|voorts constaterende|voorts overwegende),? dat\s*:",re.I)
RES=re.compile(r"\b(?:is|zijn) (?:met|bij|zonder)[^.]{0,80}(?:aangenomen|verworpen|aanvaard)|\bis ingetrokken|\bis aangehouden|\bstaken de stemmen",re.I)
def split_block(seg):
    ps=seg['text'].split('\n')
    chair=bool(re.match(r'^(DE )?V\w*O+R?Z',seg.get('name','')))
    for i,p in enumerate(ps):
        hit=False
        if GEM.match(p): hit=True
        elif CON.match(p): hit=True
        elif MOT.match(p) and ((i+1<len(ps) and GEM.match(ps[i+1])) or RES.search(p) or (len(p)<160 and i+2<len(ps) and GEM.match(ps[i+2]))): hit=True
        elif p.startswith('(Tijdens de raadsvergadering'): hit=True
        elif chair and re.match(r'^Agendapunt \d[\d.]*\s*[,:.]',p): hit=True
        if hit:
            # include a preceding short title line 'Motie 1. X'
            j=i
            for back in (1,2,3):
                if i-back>=0 and (MOT.match(ps[i-back]) or GEM.match(ps[i-back])) and all(len(x)<400 for x in ps[i-back:i]): j=i-back
            a=dict(seg); a['text']='\n'.join(ps[:j])
            b=dict(seg); b['kind']='doc'; b['text']='\n'.join(ps[j:])
            for kk in('pfx','name','pars'): b.pop(kk,None)
            return [x for x in (a,b) if x['text'].strip() or x is a and x['kind']!='sp']
    return [seg]
bydate=collections.defaultdict(lambda: collections.defaultdict(list))
for docId,segs in S.items():
    d=DOC[docId]
    if 'Motie' in d['title'][:30] or not segs: continue
    td=title_dates(d['title'])
    concept='Concept' in d['title']
    for s in segs:
        if not s['date']: s['date']=td[0] if td else None
        if not s['date']: continue
        s['concept']=concept
        s['text']=s['text'].replace('İ','I').replace('\u2028',' ')
        s['text']=re.sub(r'[\x00-\x09\x0b-\x1f]','',s['text'])
        parts=split_block(s) if s['kind'] in('sp','nar') else [s]
        for p in parts:
            if p['kind']=='nar': p['kind']='doc'
            bydate[s['date']][docId].append(p)
# ---------- dedupe per date
def norm(t): return re.sub(r'\W+','',t.lower())
kept={}
dropped=[]
for date,docs in sorted(bydate.items()):
    order=sorted(docs.items(),key=lambda kv:-sum(len(s['text']) for s in kv[1]))
    keep=[]
    for docId,segs in order:
        tot=sum(len(s['text']) for s in segs)
        if tot<200 and keep: dropped.append((date,docId,'tiny')); continue
        dup=False
        if keep:
            samples=[norm(s['text'])[20:140] for s in segs if s['kind']=='sp' and len(s['text'])>400][:60:3]
            if samples:
                for kd,ktxt in keep:
                    f=sum(1 for x in samples if x in ktxt)
                    if f>=0.6*len(samples): dup=True
            else:
                allt=norm(' '.join(s['text'] for s in segs))[:300]
                dup=any(allt[:200] in ktxt for kd,ktxt in keep)
        if dup: dropped.append((date,docId,'dup')); continue
        keep.append((docId,norm(' '.join(s['text'] for s in segs))))
    # chronological order of parts: ochtend<middag<avond, concept last
    zo={'ochtend':0,'':1,'middag':2,'avond':3,'nacht':4}
    ks=sorted([k for k,_ in keep],key=lambda k:(docs[k][0]['concept'],min(zo.get(s['zit'],1) for s in docs[k]),docs[k][0]['pg'] or 0))
    kept[date]=[(k,docs[k]) for k in ks]
for x in dropped: print('  drop',x[0],DOC[x[1]]['title'][:60])
for d,v in kept.items():
    if len(v)>1: print('  multi',d,[(DOC[k]['title'][:50],len(sg)) for k,sg in v])
print('dates',len(kept),'dropped',len(dropped),collections.Counter(x[2] for x in dropped))
# ---------- speakers
namecount=collections.Counter()
for date,dl in kept.items():
    for k,segs in dl:
        for s in segs:
            if s['kind']=='sp': namecount[key(s['name'])]+=1
canon={}
freq=[n for n,c in namecount.items() if c>=15]
for n,c in namecount.items():
    if c<15 and not re.match(r'^(DE )?V\w*O+R?Z\w*T+ERS?$',n):
        m=difflib.get_close_matches(n,freq,1,0.84)
        if m and m[0][:1]==n[:1] or (m and n.replace(' ','')==m[0].replace(' ','')): canon[n]=m[0]
canon.update({'CO KUN':'COSKUN','CECIK':'CICEK','COKUN':'COSKUN','SEGERS':'SEGERS HOOGENDOORN','WIJGENBA':'WIJBENGA VAN NIEUWENHUIZEN','MOHAMED':'MOHAMED HOESEIN','AAFJES':'AAFJES VAN AALST'})
for n in list(namecount):
    if n not in REG and n not in canon:
        c=[k for k in REG if k.startswith(n+' ') or k.endswith(' '+n)]
        if n.startswith('VAN ') and n[4:] in REG: c=[n[4:]]
        if len(c)==1 and len(n)>4 and 'VERKENNER' not in c[0]: canon[n]=c[0]
print('typo map',canon)
SPK={}; SPL=[]   # speakers: [display, sortkey]
def spk(disp,sort):
    if disp not in SPK: SPK[disp]=len(SPL); SPL.append([disp,sort])
    return SPK[disp]
PAR={}; PAL=[]
def par(p):
    if p is None: return -1
    if p not in PAR: PAR[p]=len(PAL); PAL.append(p)
    return PAR[p]
ROLES=['raadslid','voorzitter','wethouder','burgemeester','griffier','overig']
def chair_from_pre(t):
    m=re.search(r'Voorzitter\s*:\s*(?:de heer|mevrouw|dhr\.|mw\.)\s+((?:(?:drs|ing|mr|dr|ir|prof)\.\s*)*)((?:[A-Z]\.\s*)+)([A-Za-zÀ-ÿ\'\- ]+?)(?=[,.\n;(]| met | en | \(|$)',t)
    return m.group(3).strip() if m else None
BURG={'ABOUTALEB','SCHOUTEN'}
out_dates={}
unk=collections.Counter()
for date,dl in sorted(kept.items()):
    y=int(date[:4]); rows=[]; chair=None
    # majority party/role per name in this date for inheritance
    maj=collections.defaultdict(collections.Counter)
    for k,segs in dl:
        for s in segs:
            if s['kind']=='sp' and s['pars']:
                maj[canon.get(key(s['name']),key(s['name']))][tuple(s['pars'])]+=1
    for k,segs in dl:
        for s in segs:
            if s['kind']=='pre':
                c=chair_from_pre(s['text']); chair=c or chair
                if not s['text'].strip(): continue
                rows.append((s,-1,-1,5,'')); continue
            if s['kind'] in('doc','hd'):
                if s['kind']=='hd': continue
                if not s['text'].strip(): continue
                rows.append((s,-1,-1,5,'')); continue
            nk=key(s['name']); nk=canon.get(nk,nk)
            pars=s['pars'] or (list(maj[nk].most_common(1)[0][0]) if maj.get(nk) and not re.match(r'^(DE )?V\w*O+R?Z',nk) and nk!='GRIFFIER' else [])
            party=None; role=None; func=''
            if re.match(r'^(DE )?V\w*O+R?Z\w*T+ERS?$|^VICEOORZITTER$',nk):
                role='voorzitter'; cn=None
                for p in s['pars']:
                    m=re.match(r'^(?:de heer|mevrouw|mw\.|dhr\.)?\s*\(?(?:[A-Z]\.\s*)*(.+)$',p,re.I)
                    if m: cn=m.group(1).split('.')[0].strip()
                cn=cn or chair
                if cn:
                    ck=key(cn); ck=canon.get(ck,ck)
                    if ck not in REG:
                        mm_=difflib.get_close_matches(ck,list(REG),1,0.8)
                        if mm_: ck=mm_[0]
                    pr=person(ck,y)
                    disp=pr[0] if pr else tcase(cn,True); sort=ck
                else: disp='Voorzitter'; sort='VOORZITTER'
            elif nk in('GRIFFIER','GRIFIER'):
                role='griffier'; disp='Griffier'; sort='GRIFFIER'
            else:
                for p in pars:
                    pl=p.lower().strip()
                    if pl in PARTY: party=PARTY[pl]; role=role or 'raadslid'
                    elif pl in('wethouder','locoburgemeester','cda wethouder'): role='wethouder'
                    elif pl=='burgemeester': role='burgemeester'
                    elif 'griffier' in pl: role='griffier'
                    elif len(pl)<60: func=p; role=role or 'overig'
                if nk in BURG and not party and role in(None,'overig'): role='burgemeester'
                if nk in('BURGEMEESTER',): role='burgemeester'
                pr=person(nk,y)
                if pr:
                    disp=pr[0]; e=pr[2]
                    if role is None:
                        rc=collections.Counter()
                        for (yy,r),c in e['role'].items():
                            if abs(yy-y)<=1 and r!='voorzitter': rc[r]+=c
                        role=rc.most_common(1)[0][0] if rc else 'overig'
                    if party is None and role=='raadslid':
                        pc=collections.Counter()
                        for (yy,p),c in e['party'].items():
                            if abs(yy-y)<=1: pc[p]+=c
                        if pc: party=pc.most_common(1)[0][0]
                else:
                    disp=tcase(s['name'].replace('- ','-'),True); unk[disp]+=1
                    if role is None: role='overig'
                sort=re.sub(r'^(VAN DER|VAN DEN|VAN DE|VAN|DE|DEN|EL|TER|LA) ','',nk)
                if func and role=='overig' and not pr: disp+=' ('+func+')'
            rows.append((s,spk(disp,sort),par(party),ROLES.index(role),func))
    out_dates[date]=(dl,rows)
print('speakers',len(SPL),'parties',PAL)
print('unknown (not in timeline registry):',len(unk),unk.most_common(60))
import pickle
pickle.dump({'out':out_dates,'SPL':SPL,'PAL':PAL,'ROLES':ROLES,'TL':TL},open('built.pkl','wb'))
kc=collections.Counter(); tc=collections.Counter()
for d,(dl,rows) in out_dates.items():
    for s,sp,pa,ro,f in rows: kc[(d[:4],s['kind'])]+=1; tc[(d[:4],s['kind'])]+=len(s['text'])
print(sorted(kc.items())); print({k:round(v/1e6,1) for k,v in sorted(tc.items())})
