"""Test van de meetlaag (docs/meet.js) in echte Chromium tegen de echte pagina's.
Start eerst een server:  python3 -m http.server 8774 -d docs
Draai:                   python3 src/test_meet_browser.py
Deel A (debug-modus): gebeurtenissen en virtuele paden op echte pagina's, deellinks met utm, deelpagina stuurt utm door.
Deel B (actief): raadzoeker.nl wordt naar localhost gemapt, host+id worden in meet.js ingevuld en de Umami-tracker is een
nagebouwde stub die data-before-send aanroept zoals Umami doet. Controleert dat NIETS de deur uitgaat met een zoekterm,
hash of query. De logica zelf wordt ook los getest in src/test_meet.js (jsdom).
"""
import json, re
from playwright.sync_api import sync_playwright

LOKAAL = 'http://localhost:8774/'
NEP = 'http://raadzoeker.nl:8774/'
RUSTIG = ("try{localStorage.setItem('rz-welkom','nee');for(const k of ['startpagina','zoek','dossier','vergadering','wijk','lab',"
          "'domeinen','verkenner','beloofd','over','hulp'])localStorage.setItem('rz-tour-'+k,'ja');}catch(e){}")
RES = []
FOUTEN = []
PROD = open('docs/meet.js', encoding='utf8').read()


def leeg(s):
    """productieconfig -> lege config, zodat de test niet afhangt van host en id in meet.js"""
    s = re.sub(r"(const CONF=\{[\s\S]*?)host:'[^']*'", r"\1host:''", s, count=1)
    return re.sub(r"(const CONF=\{[\s\S]*?)\bid:'[^']*'", r"\1id:''", s, count=1)


def uitslag(naam, ok, tekst=''):
    RES.append((naam, ok))
    print(('OK   ' if ok else 'FOUT ') + naam + (' :: ' + str(tekst)[:240] if tekst != '' else ''))


def pagina(ctx, naam):
    p = ctx.new_page()
    p.on('console', lambda m: FOUTEN.append((naam, 'console', m.text)) if m.type == 'error' else None)
    p.on('pageerror', lambda e: FOUTEN.append((naam, 'pageerror', str(e))))
    # klikken op links mag de pagina niet verlaten (na onze luisteraar, die in de capture-fase zit)
    p.add_init_script("document.addEventListener('click',e=>{if(e.target.closest&&e.target.closest('a[href]')&&!e.target.closest('[data-navigeer]'))e.preventDefault();});")
    return p


def log(p):
    return p.evaluate("(window.rzMeet&&window.rzMeet.log)||[]")


def wacht_op(p, expr, ms=25000):
    try:
        p.wait_for_function(expr, timeout=ms)
        return True
    except Exception:
        return False


STUB = """(function(){var s=document.currentScript,fn=s.dataset.beforeSend,C=window.__calls=[];
function basis(){return {website:s.dataset.websiteId,hostname:location.hostname,url:location.pathname+location.search+location.hash,title:document.title,referrer:document.referrer};}
function send(type,payload){var p=Object.assign(basis(),payload);if(fn&&window[fn])p=window[fn](type,p);if(p)C.push([type,p]);}
window.umami={track:function(a,b){if(typeof a==='string')send('event',{name:a,data:b});else if(typeof a==='function')send('event',a(basis()));else send('event',{});}};})();"""


def main():
    with sync_playwright() as pw:
        # ---------------- deel A: debug-modus op echte pagina's ----------------
        b = pw.chromium.launch()
        ctx = b.new_context(viewport={'width': 1280, 'height': 900})
        ctx.add_init_script(RUSTIG + "try{localStorage.setItem('rz-meetdebug','1');}catch(e){}")
        ctx.route(re.compile(r'.*/meet\.js.*'), lambda r: r.fulfill(status=200, content_type='application/javascript', body=leeg(PROD)))

        p = pagina(ctx, 'start')
        p.goto(LOKAAL + 'index.html')
        uitslag('A1 startpagina: meet.js geladen, debug-modus, pageview "/"',
                wacht_op(p, "window.rzMeet&&window.rzMeet.log&&window.rzMeet.log.length>0", 8000) and ['pageview', '/'] in log(p), log(p)[:3])

        p = pagina(ctx, 'dossier')
        p.goto(LOKAAL + 'dossier.html#parkeren')
        wacht_op(p, "document.querySelector('[data-volg]')", 20000)
        pv = [x[1] for x in log(p) if x[0] == 'pageview']
        uitslag('A2 dossier: virtueel pad /dossier/parkeren', pv[:1] == ['/dossier/parkeren'], pv)
        # volgen
        if p.query_selector('[data-volg]'):
            p.click('[data-volg]')
            p.wait_for_timeout(250)
            uitslag('A3 volgen: gebeurtenis met slug en aan-stand',
                    any(x[0] == 'volg' and x[1].get('slug') == 'parkeren' and 'aan' in x[1] for x in log(p)), [x for x in log(p) if x[0] == 'volg'])
        else:
            uitslag('A3 volgen: gebeurtenis met slug en aan-stand', False, 'geen [data-volg] op de pagina')
        # kopieerknop
        kn = p.query_selector('button[data-rzc]')
        if kn:
            soort = kn.get_attribute('data-rzc')
            kn.evaluate('e=>e.click()')
            p.wait_for_timeout(250)
            uitslag('A4 kopieerknop: gebeurtenis met soort en pagina', any(x[0] == 'kopieer' and x[1].get('soort') == soort and x[1].get('pagina') == 'dossier' for x in log(p)), soort)
        else:
            uitslag('A4 kopieerknop: gebeurtenis met soort en pagina', False, 'geen knop gevonden')
        # deellinks krijgen utm
        wacht_op(p, "document.querySelector('a[href^=\"mailto:?subject\"]')", 8000)
        hrefs = p.evaluate("[...document.querySelectorAll('a[href^=\"mailto:?subject\"],a[href*=\"teams.microsoft.com/share\"],a[href^=\"https://wa.me/\"]')].map(a=>decodeURIComponent(a.href))")
        kanalen = {k: any(('utm_medium=' + k) in h and 'utm_source=deel' in h for h in hrefs) for k in ['mail', 'teams', 'whatsapp']}
        uitslag('A5 deellinks (mail, teams, whatsapp) dragen utm_source=deel en utm_medium', all(kanalen.values()), kanalen)
        # externe link
        ext = p.query_selector('a[href^="http"]:not([href*="raadzoeker.nl"]):not([href*="teams.microsoft.com"]):not([href*="wa.me"])')
        if ext:
            doel = ext.evaluate("a=>new URL(a.href).hostname")
            ext.evaluate('a=>a.click()')   # JS-klik: de eerste externe link kan in een ingeklapt blok zitten
            p.wait_for_timeout(250)
            uitslag('A6 externe link: gebeurtenis uitgaand met groep', any(x[0] == 'uitgaand' for x in log(p)), [x for x in log(p) if x[0] == 'uitgaand'][:1] or doel)
        else:
            uitslag('A6 externe link: gebeurtenis uitgaand met groep', True, 'geen externe link op deze pagina (overgeslagen)')
        # hash naar ander dossier
        p.evaluate("location.hash='#wonen-en-bouwen'")
        p.wait_for_timeout(300)
        pv = [x[1] for x in log(p) if x[0] == 'pageview']
        uitslag('A7 hashchange naar ander dossier geeft nieuwe pageview', pv[-1:] == ['/dossier/wonen-en-bouwen'], pv)

        # zoeken
        p = pagina(ctx, 'zoek')
        p.goto(LOKAAL + 'zoek.html#q=parkeren')
        ok = wacht_op(p, "(window.rzMeet.log||[]).some(x=>x[0]==='zoek')", 30000)
        z = [x for x in log(p) if x[0] == 'zoek']
        uitslag('A8 zoeken: gebeurtenis zoek met aantal, zonder zoekterm', ok and z and z[0][1].get('n', 0) > 0 and z[0][1].get('leeg') is False and 'q' not in z[0][1], z[:1])
        uitslag('A9 zoeken: pageview is /zoeken (geen zoekterm in het pad)', [x[1] for x in log(p) if x[0] == 'pageview'][:1] == ['/zoeken'])
        tab = p.query_selector('#tabs [data-tab="stukken"]')
        if tab:
            tab.click()
            p.wait_for_timeout(300)
            uitslag('A10 tab Stukken: gebeurtenis zoek_tab', any(x[0] == 'zoek_tab' and x[1].get('tab') == 'stukken' for x in log(p)))
        alles = json.dumps(log(p))
        uitslag('A11 zoeken: nergens de zoekterm "parkeren" in de gebeurtenissen van Zoeken', 'parkeren' not in alles.lower(), alles[:200])

        # Over: privacytekst verborgen zolang de meting uit staat
        p = pagina(ctx, 'over')
        p.goto(LOKAAL + 'over.html')
        p.wait_for_timeout(500)
        uitslag('A12 Over: privacyregel over meten is verborgen zolang meet.js geen host heeft',
                p.evaluate("document.getElementById('meetpriv').hidden===true && document.getElementById('meetfaq').hidden===true"))

        # deelpagina stuurt utm door
        p = ctx.new_page()
        p.goto(LOKAAL + 'deel/parkeren.html?utm_source=deel&utm_medium=teams', wait_until='commit')
        wacht_op(p, "location.pathname.endsWith('dossier.html')", 10000)
        uitslag('A13 deelpagina stuurt door naar het dossier met utm vóór de hash',
                bool(re.search(r'/dossier\.html\?utm_source=deel&utm_medium=teams#parkeren$', p.url)), p.url)
        p = ctx.new_page()
        p.goto(LOKAAL + 'deel/parkeren.html', wait_until='commit')
        wacht_op(p, "location.pathname.endsWith('dossier.html')", 10000)
        uitslag('A14 deelpagina zonder query werkt nog gewoon', p.url.endswith('/dossier.html#parkeren'), p.url)
        b.close()

        # ---------------- deel B: actief, met nagebouwde tracker ----------------
        b = pw.chromium.launch(args=['--host-resolver-rules=MAP raadzoeker.nl 127.0.0.1, MAP stats.test 127.0.0.1'])
        ctx = b.new_context(viewport={'width': 1280, 'height': 900})
        ctx.add_init_script(RUSTIG)
        meet = leeg(PROD).replace("host:''", "host:'https://stats.test'").replace("id:''", "id:'site-123'")
        ctx.route(re.compile(r'.*/meet\.js.*'), lambda r: r.fulfill(status=200, content_type='application/javascript', body=meet))
        ctx.route('https://stats.test/script.js', lambda r: r.fulfill(status=200, content_type='application/javascript', body=STUB))

        p = pagina(ctx, 'actief-zoek')
        p.goto(NEP + 'zoek.html?q=geheime+zoekterm#q=geheime+zoekterm')
        ok = wacht_op(p, "window.__calls&&window.__calls.some(c=>c[1].name==='zoek')", 30000)
        calls = p.evaluate("window.__calls||[]")
        uitslag('B1 tracker geladen en gebeurtenis zoek aangekomen', ok, [c[1].get('name') or c[1].get('url') for c in calls][:5])
        urls = [c[1].get('url', '') for c in calls]
        uitslag('B2 geen enkele verzending met zoekterm, query of hash in de url',
                all(u.startswith('/') and '?' not in u.split('?utm_')[0] and '#' not in u and 'geheim' not in u for u in urls), urls)
        uitslag('B3 pagina is /zoeken en titel is het pad', calls and calls[0][1]['url'] == '/zoeken' and calls[0][1]['title'] == '/zoeken', calls[:1])
        tekst = json.dumps(calls).lower()
        uitslag('B4 de zoekterm komt nergens voor in wat verstuurd is', 'geheim' not in tekst, tekst[:200])
        uitslag('B5 website-id en hostname meegestuurd', all(c[1].get('website') == 'site-123' and c[1].get('hostname') == 'raadzoeker.nl' for c in calls))

        p = pagina(ctx, 'actief-dossier')
        p.goto(NEP + 'dossier.html?utm_source=deel&utm_medium=teams#parkeren')
        wacht_op(p, "window.__calls&&window.__calls.length>0", 15000)
        c0 = p.evaluate("window.__calls[0]")
        uitslag('B6 deelbezoek: utm blijft in de url, rest niet', c0 and c0[1]['url'] == '/dossier/parkeren?utm_source=deel&utm_medium=teams', c0)

        # opt-out: ?meet=uit
        p = pagina(ctx, 'uit')
        p.goto(NEP + 'dossier.html?meet=uit#parkeren')
        p.wait_for_timeout(1500)
        uitslag('B7 ?meet=uit: tracker niet geladen, geen verzending',
                p.evaluate("typeof window.umami==='undefined' && !window.__calls"))
        p.goto(NEP + 'over.html?meet=aan')
        wacht_op(p, "document.getElementById('meetpriv')&&!document.getElementById('meetpriv').hidden", 8000)
        uitslag('B8 Over: privacyregel zichtbaar zodra de meting aan staat, met keuzeknop',
                p.evaluate("(()=>{const l=document.getElementById('meetpriv');return !l.hidden && !!l.querySelector('#meetknop') && /Umami/.test(l.textContent);})()"))
        b.close()

    print('\n=== console- en paginafouten ===')
    echte = []
    for naam, soort, tekst in FOUTEN:
        if '/api/' in tekst or '501' in tekst or 'ERR_NAME_NOT_RESOLVED' in tekst or 'net::ERR' in tekst or '404' in tekst:
            print(f'  (genegeerd) [{naam}] {soort}: {tekst[:150]}')
        else:
            print(f'  [{naam}] {soort}: {tekst[:200]}'); echte.append(tekst)
    uitslag('Z geen console- of paginafouten (zonder /api/ en netwerk naar nepdomeinen)', not echte, echte[:2])
    mis = [n for n, ok in RES if not ok]
    print(f'\n{sum(1 for _, ok in RES if ok)} van {len(RES)} controles geslaagd' + (f'; mislukt: {mis}' if mis else ''))
    raise SystemExit(1 if mis else 0)


if __name__ == '__main__':
    main()
