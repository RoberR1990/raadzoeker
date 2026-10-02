# Rustige iBabs-ophaler: max 1 verzoek per seconde, met cache in WERK/ibabs/cache (zelfde URL wordt niet opnieuw opgehaald).
# Stopt bij een blokkade (403/429/captcha) in plaats van door te gaan.
import os,time,hashlib,urllib.request,urllib.error,urllib.parse,json
from paden import WERK
BASE='https://gemeenteraad.rotterdam.nl'
CACHE=os.path.join(WERK,'ibabs','cache'); os.makedirs(CACHE,exist_ok=True)
UA='Raadzoeker/1.0 (onderzoekstool; contact rriteco@gmail.com)'
_last=[0.0]
class Blokkade(Exception): pass
def get(url,binary=False,cache=True,data=None):
    if url.startswith('/'): url=BASE+url
    body=urllib.parse.urlencode(data).encode() if data is not None else None
    p=os.path.join(CACHE,hashlib.sha1(url.encode()+(b'|'+body if body else b'')).hexdigest())
    if cache and os.path.exists(p):
        b=open(p,'rb').read(); return b if binary else b.decode('utf8','replace')
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
def report(rid,start=0,length=500):
    """Eén pagina uit een iBabs-rapportage (DataTables server-side)."""
    d={'draw':'1','start':str(start),'length':str(length),'order[0][column]':'0','order[0][dir]':'asc','search[value]':'','search[regex]':'false'}
    return json.loads(get(f'/Reports/GetReportData/{rid}',data=d))
def report_all(rid,length=100):
    # de server geeft hooguit 100 rijen per keer, ook als je meer vraagt
    out=[];start=0
    while True:
        r=report(rid,start,length); out+=r['data']; start+=len(r['data'])
        if start>=r['recordsFiltered'] or not r['data']: return out,r
