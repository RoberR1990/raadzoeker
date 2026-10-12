# Sprekerstijdlijn uit iBabs ontleden (zonder bronbestanden; gedeeld door build.py en debat_nieuw.py).
import re,unicodedata
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
ROLEW=['Plaatsvervangende voorzitter','Plv. commissievoorzitter','Plaatsvervangend voorzitter','Plaatsvervangend griffier','Commissievoorzitter','Burgercommissielid','Kandidaat-wethouder','Nestor van de gemeenteraad','Fractievoorzitter','Informateur','Inspreker','Raadslid','Voorzitter','Wethouder','Burgemeester','Griffier','Burgerlid','COR-lid']
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
