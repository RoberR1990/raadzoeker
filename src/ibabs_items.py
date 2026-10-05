# Haalt detailpagina's (en bij moties/amendementen de pdf-tekst van het hoofddocument) op uit iBabs.
# Invoer: WERK/ibabs/lijsten.json (ibabs_lijsten.py). Uitvoer: WERK/ibabs/items_<soort>.jsonl, hervatbaar.
# Gebruik: python src/ibabs_items.py toezeggingen moties amendementen raadsvoorstellen initiatiefvoorstellen [--ververs-open] [--minuten N]
#   --ververs-open: ook de detailpagina's van nog niet afgedane stukken opnieuw ophalen (nachtelijke run)
# Alleen stukken vanaf VANAF (2018). Max 1 verzoek per seconde (ibabs.get); stopt bij een blokkade.
import json,os,re,sys,html,time
import ibabs
from paden import WERK
VANAF=2018
STOP=None   # --minuten N: netjes stoppen na N minuten (hervatbaar)
ALLEEN=None   # --alleen REGEX: alleen stukken waarvan de titel matcht (gericht ophalen)
class TijdOp(Exception): pass
PDF={'moties','amendementen','initiatiefvoorstellen','wijkraadadviezen','brieven'}
def tekst(s): return re.sub(r'[ \t]+',' ',html.unescape(re.sub(r'<[^>]+>',' ',s))).strip()
def parse(h):
    b=h[h.find('id="maincontent"'):h.find('<footer')]
    d={}
    for dt,dd in re.findall(r'<dt[^>]*>(.*?)</dt>\s*<dd[^>]*>(.*?)</dd>',b,re.S):
        k=tekst(dt)
        docs=[{'url':html.unescape(u),'naam':re.sub(r'\s+',' ',tekst(n))} for u,n in re.findall(r'<a href="(/Reports/Document/[^"]+)"[^>]*>(.*?)</a>',dd,re.S)]
        rel=[{'id':u,'naam':re.sub(r'\s+',' ',tekst(n))} for u,n in re.findall(r'<a href="/Reports/Item/([^"]+)"[^>]*>(.*?)</a>',dd,re.S)]
        if docs: d[k]=docs
        elif rel: d[k]=rel
        else:
            sr=re.search(r'class="sr-only">([^<]*)<',dd)
            v=sr.group(1).strip() if sr else re.sub(r'\n\s*',' \n',tekst(re.sub(r'<li[^>]*>',' | ',dd))).strip(' |\n')
            if sr: v=not v.lower().startswith('niet')
            d[k]=v
    return d
def jaar(r):
    m=re.search(r'(\d{4})\s*$',(r.get('registrationdate') or r.get('datumbesluit') or '').strip())
    return int(m.group(1)) if m else None
def pdftekst(url,base=''):
    import pymupdf
    # /Reports/Document/... is een viewer; de pdf zelf staat op /Document/View/{documentId}
    b=ibabs.get(base+'/Document/View/'+re.search(r'documentId=([0-9a-f-]+)',url).group(1),binary=True)
    if not b.startswith(b'%PDF'): return None
    with pymupdf.open(stream=b,filetype='pdf') as doc: return '\n'.join(p.get_text() for p in doc).strip()
def soort(naam,rows):
    out=os.path.join(WERK,'ibabs',f'items_{naam}.jsonl')
    klaar=set()
    if os.path.exists(out):
        goed=[]
        for l in open(out,encoding='utf8'):
            try: klaar.add(json.loads(l)['id']); goed.append(l)
            except Exception: pass   # half geschreven regel na een onderbreking
        open(out,'w',encoding='utf8').writelines(goed)
    todo=[r for r in rows if (jaar(r) or 0)>=VANAF and r['DT_RowId'] not in klaar and (not ALLEEN or re.search(ALLEEN,(r.get('title') or '').lower()))]
    print(naam,'te doen',len(todo),'al klaar',len(klaar),flush=True)
    t0=time.time()
    with open(out,'a',encoding='utf8') as f:
        for k,r in enumerate(todo):
            d={'id':r['DT_RowId'],'lijst':r,'detail':parse(ibabs.get('/Reports/Item/'+r['DT_RowId']))}
            if naam in PDF:
                hd=d['detail'].get('Hoofddocument') or d['detail'].get('Document')
                if isinstance(hd,list) and hd:
                    try: d['tekst']=pdftekst(hd[0]['url'])
                    except ibabs.Blokkade: raise
                    except Exception as e: d['tekstfout']=str(e)[:200]
            f.write(json.dumps(d,ensure_ascii=False)+'\n'); f.flush()
            if k%200==0: print(naam,k,'/',len(todo),round((time.time()-t0)/60),'min',flush=True)
            if STOP and time.time()>STOP: raise TijdOp()
def ververs_open(naam,rows,dagen=1200):
    """Detailpagina's opnieuw ophalen van stukken die nog niet zijn afgedaan (status, tussenberichten, afdoening), van de laatste `dagen`.
    Nieuwe stukken haalt soort() op; dit houdt de bestaande actueel."""
    import datetime
    out=os.path.join(WERK,'ibabs',f'items_{naam}.jsonl')
    if not os.path.exists(out): return
    regels=[json.loads(l) for l in open(out,encoding='utf8') if l.strip()]
    lijst={r['DT_RowId']:r for r in rows}; grens=(datetime.date.today()-datetime.timedelta(days=dagen)).isoformat()
    def iso(x): m=re.match(r'\s*(\d\d)-(\d\d)-(\d{4})',x or ''); return f'{m.group(3)}-{m.group(2)}-{m.group(1)}' if m else ''
    todo=[i for i,d in enumerate(regels) if not d['detail'].get('Afgedaan') and not d['detail'].get('Datum afgedaan') and iso(d['lijst'].get('registrationdate'))>=grens]
    print(naam,'open om te verversen',len(todo),flush=True)
    try:
        for n,i in enumerate(todo):
            d=regels[i]; d['detail']=parse(ibabs.get('/Reports/Item/'+d['id'],cache=False)); d['lijst']=lijst.get(d['id'],d['lijst'])
            if STOP and time.time()>STOP: raise TijdOp()
    finally:
        tmp=out+'.tmp'; open(tmp,'w',encoding='utf8').write(''.join(json.dumps(d,ensure_ascii=False)+'\n' for d in regels)); os.replace(tmp,out)
if __name__=='__main__':
    L=json.load(open(os.path.join(WERK,'ibabs','lijsten.json'),encoding='utf8'))
    args=sys.argv[1:]
    if '--minuten' in args:
        i=args.index('--minuten'); STOP=time.time()+60*float(args[i+1]); del args[i:i+2]
    if '--alleen' in args:
        i=args.index('--alleen'); ALLEEN=args[i+1]; del args[i:i+2]
    VERS='--ververs-open' in args
    if VERS: args.remove('--ververs-open')
    try:
        for naam in args:
            soort(naam,L[naam])
            if VERS: ververs_open(naam,L[naam])
    except TijdOp:
        print('tijd op, later verder',flush=True); sys.exit(0)
    except ibabs.Blokkade as e:
        print('BLOKKADE, gestopt:',e,flush=True); sys.exit(2)
    print('klaar',flush=True)
