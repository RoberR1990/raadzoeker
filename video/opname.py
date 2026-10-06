# Schermafbeeldingen van de echte site voor de promovideo (Playwright + Edge, 1920x1080, 2x scherp).
#   python video/opname.py deel1   -> video/public/shots/*.png + shots.json (plekken van knoppen voor de cursor)
# Vereist een lokale server: python -m http.server 8765 -d docs
import json,os,sys,time
from playwright.sync_api import sync_playwright
BASE='http://localhost:8765/ontwerp/'
UIT=os.path.join(os.path.dirname(__file__),'public','shots'); os.makedirs(UIT,exist_ok=True)
INFO={}
def doos(page,sel):
    b=page.locator(sel).first.bounding_box()
    return [round(b['x']),round(b['y']),round(b['width']),round(b['height'])] if b else None
def foto(page,naam,**kw):
    page.wait_for_timeout(400); page.screenshot(path=os.path.join(UIT,naam+'.png'),**kw); print(naam)
def klaar(page):
    page.add_init_script("try{localStorage.setItem('rz-welkom','nee');['vergaderingen','vergadering','zoek','dossier','wijk','verkenner','lab','domeinen','startpagina'].forEach(p=>localStorage.setItem('rz-tour-'+p,'ja'));}catch(e){}")
def deel1(page):
    # 1 overzicht Vergaderingen
    page.goto(BASE+'vergaderingen.html'); page.wait_for_selector('#hero h2'); page.wait_for_timeout(1500)
    foto(page,'d1_overzicht'); INFO['d1_overzicht']={'hero':doos(page,'#hero .knop'),'komt':doos(page,'#komt')}
    # 2 korte samenvatting
    page.evaluate("localStorage.setItem('rz-vmodus','kort')")
    page.goto(BASE+'vergadering.html?id=9f0ee187'); page.wait_for_selector('.kort .zin'); page.wait_for_timeout(1200)
    foto(page,'d1_kort'); INFO['d1_kort']={'schakel':doos(page,'.schakel [data-m=uitgebreid]')}
    # 3 uitgebreid: fractie aantikken -> citaat -> videomoment
    page.evaluate("localStorage.setItem('rz-vmodus','uitgebreid')"); page.goto(BASE+'vergadering.html?id=9f0ee187&u=1#ap-9.2'); page.wait_for_selector('#ap-9\\.2 .pt'); page.wait_for_timeout(800)
    page.evaluate("document.querySelector('#ap-9\\\\.2 h3').scrollIntoView({block:'start'});window.scrollBy(0,-90)"); page.wait_for_timeout(600)
    foto(page,'d1_fracties'); pt='#ap-9\\.2 .pt:not(.coll)'; INFO['d1_fracties']={'pt':doos(page,pt)}
    page.locator(pt).first.click(); page.wait_for_timeout(700)
    foto(page,'d1_citaat'); INFO['d1_citaat']={'speel':doos(page,'#ap-9\\.2 .cit [data-video]')}
    page.locator('#ap-9\\.2 .cit [data-video]').first.click(); page.wait_for_timeout(9000)
    foto(page,'d1_video')
    # 4 moties met uitslag en tijdlijn (raad 10 september, agendapunt 7.1)
    page.goto(BASE+'vergadering.html?id=c3deba48#ap-7.1'); page.wait_for_selector('#ap-7\\.1 .mo'); page.wait_for_timeout(800)
    page.evaluate("document.querySelector('#ap-7\\\\.1 .apmeta').scrollIntoView({block:'start'});window.scrollBy(0,-120)"); page.wait_for_timeout(600)
    foto(page,'d1_moties'); INFO['d1_moties']={'mo':doos(page,'#ap-7\\.1 .mo'),'spoor':doos(page,'#ap-7\\.1 .spoor'),'tijd':doos(page,'#ap-7\\.1 .apmeta')}
if __name__=='__main__':
    with sync_playwright() as p:
        b=p.chromium.launch(channel='msedge',headless=True)
        ctx=b.new_context(viewport={'width':1920,'height':1080},device_scale_factor=2,locale='nl-NL',timezone_id='Europe/Amsterdam')
        page=ctx.new_page(); klaar(page)
        {'deel1':deel1}[sys.argv[1]](page)
        b.close()
    pj=os.path.join(UIT,'shots.json'); A=json.load(open(pj)) if os.path.exists(pj) else {}
    A.update(INFO); json.dump(A,open(pj,'w'),indent=1)
