# Rustige iBabs-ophaler: max 1 verzoek per seconde, met cache in WERK/ibabs/cache (zelfde URL wordt niet opnieuw opgehaald).
# Stopt bij een blokkade (403/429/captcha) in plaats van door te gaan.
import os,time,hashlib,urllib.request,urllib.error,urllib.parse,json
from paden import WERK
BASE='https://gemeenteraad.rotterdam.nl'
CACHE=os.path.join(WERK,'ibabs','cache'); os.makedirs(CACHE,exist_ok=True)
UA='Raadzoeker/1.0 (onderzoekstool; contact github.com/RoberR1990/raadzoeker)'
_last=[0.0]
class Blokkade(Exception): pass
SLOT=os.path.join(WERK,'ibabs','.slot'); STEMPEL=os.path.join(WERK,'ibabs','.laatste')
def _beurt_ibabs():
    """Max 1 verzoek per 1,05 s naar iBabs, ook als er meerdere processen lopen (lockbestand + tijdstempel)."""
    while True:
        try: fd=os.open(SLOT,os.O_CREAT|os.O_EXCL|os.O_WRONLY); break
        except (FileExistsError,PermissionError):   # Windows: slot wordt net verwijderd
            try:
                if time.time()-os.path.getmtime(SLOT)>30: os.remove(SLOT)   # achtergebleven slot
            except OSError: pass
            time.sleep(0.05)
    try:
        try: last=float(open(STEMPEL).read())
        except Exception: last=0.0
        wait=1.05-(time.time()-last)
        if wait>0: time.sleep(wait)
        open(STEMPEL,'w').write(str(time.time()))
    finally:
        os.close(fd); os.remove(SLOT)
def get(url,binary=False,cache=True,data=None):
    if url.startswith('/'): url=BASE+url
    body=urllib.parse.urlencode(data).encode() if data is not None else None
    p=os.path.join(CACHE,hashlib.sha1(url.encode()+(b'|'+body if body else b'')).hexdigest())
    if cache and os.path.exists(p):
        b=open(p,'rb').read(); return b if binary else b.decode('utf8','replace')
    if 'ibabs' in url or 'rotterdam.nl' in url and ('gemeenteraad.' in url or 'wijkraad.' in url):
        _beurt_ibabs()   # gedeelde limiet voor alle iBabs-hosts, over processen heen
    else:
        wait=1.05-(time.time()-_last[0])
        if wait>0: time.sleep(wait)
        _last[0]=time.time()
    req=urllib.request.Request(url,data=body,headers={'User-Agent':UA,'Accept-Language':'nl','X-Requested-With':'XMLHttpRequest'} if body else {'User-Agent':UA,'Accept-Language':'nl'})
    try:
        with urllib.request.urlopen(req,timeout=60) as r: b=r.read()
    except urllib.error.HTTPError as e:
        if e.code in(403,429,503): raise Blokkade(f'{e.code} op {url}')
        raise
    if b'captcha' in b[:20000].lower() or b'cf-challenge' in b[:20000]: raise Blokkade('captcha/challenge op '+url)
    if cache: open(p,'wb').write(b)
    return b if binary else b.decode('utf8','replace')
def report(rid,start=0,length=500,base=BASE):
    """Eén pagina uit een iBabs-rapportage (DataTables server-side)."""
    d={'draw':'1','start':str(start),'length':str(length),'order[0][column]':'0','order[0][dir]':'asc','search[value]':'','search[regex]':'false'}
    return json.loads(get(f'{base}/Reports/GetReportData/{rid}',data=d))
def report_all(rid,length=100,base=BASE):
    # de server geeft hooguit 100 rijen per keer, ook als je meer vraagt
    out=[];start=0
    while True:
        r=report(rid,start,length,base); out+=r['data']; start+=len(r['data'])
        if start>=r['recordsFiltered'] or not r['data']: return out,r
