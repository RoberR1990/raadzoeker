"""Test citeren in één klik en 'Kopieer voor Copilot' (docs/citeer.js).
Start eerst een server:  python3 -m http.server 8771 -d docs
Draai:                   python3 src/test_citeer.py
"""
import json, os, re, sys
from playwright.sync_api import sync_playwright

BASE = 'http://localhost:8771/'
SHOTS = '/tmp/claude-0/-home-claude/27462a42-c492-5a46-80c7-d7eb1ac7cf72/scratchpad/citeer/'
os.makedirs(SHOTS, exist_ok=True)
# geen welkomstvenster of rondleidingsbalk tijdens de test
RUSTIG = "try{localStorage.setItem('rz-welkom','nee');for(const k of ['startpagina','zoek','dossier','vergadering','wijk','lab','domeinen','verkenner'])localStorage.setItem('rz-tour-'+k,'ja');}catch(e){}"
RES = []
FOUTEN = []


def uitslag(naam, ok, tekst=''):
    RES.append((naam, ok))
    print(('OK   ' if ok else 'FOUT ') + naam + (' :: ' + tekst if tekst else ''))


def nieuwe_pagina(ctx, url, naam=None):
    p = ctx.new_page()
    p.on('console', lambda m: FOUTEN.append((naam or url, 'console', m.text)) if m.type == 'error' else None)
    p.on('pageerror', lambda e: FOUTEN.append((naam or url, 'pageerror', str(e))))
    p.goto(BASE + url)
    return p


def klembord(p):
    return p.evaluate('navigator.clipboard.readText()')


def wacht_treffers(p, n=1):
    p.wait_for_function(f"document.querySelectorAll('#uit article.res').length>={n}", timeout=60000)


def schoon(t):
    return re.sub(r'\s+', ' ', t.replace('…', ' ')).strip()


CIT_RE = re.compile(
    r"^‘(?P<t>.+)’\n— (?P<wie>[^\n]+?), (?P<org>[^\n]+?) Rotterdam, (?P<d>\d{1,2} [a-z]+ \d{4})(?:, agendapunt(?: \S+)?(?: ‘[^\n]+’)?)?"
    r"(?:, automatische ondertiteling \(kan fouten bevatten\))?(?:, video ca\. \d:\d\d:\d\d)?\n"
    r"(?:Bron: https://gemeenteraad\.rotterdam\.nl/Agenda/Index/[0-9a-f-]+\n)?Fragment: https://raadzoeker\.nl/zoek\.html#b=\S+$", re.S)


def kaart_info(p, i):
    """tekst van het getoonde fragment en de spreker van kaart i"""
    return p.evaluate("""i=>{const a=document.querySelectorAll('#uit article.res')[i];
      return {fr:a.querySelector('.fr').textContent.replace(/^‘|’$/g,''),wie:a.querySelector('.m b').textContent,meta:a.querySelector('.m').textContent};}""", i)


def main():
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        ctx = br.new_context(viewport={'width': 1280, 'height': 900}, locale='nl-NL')
        ctx.grant_permissions(['clipboard-read', 'clipboard-write'], origin='http://localhost:8771')
        ctx.add_init_script(RUSTIG)

        # ---------- (a) citaat uit zoek.html#q=parkeren ----------
        p = nieuwe_pagina(ctx, 'zoek.html#q=parkeren', 'zoek')
        wacht_treffers(p)
        p.wait_for_selector('#copbtn:not([hidden])')
        uitslag('a1 treffers geladen', p.locator('#uit article.res').count() >= 5, str(p.locator('#uit article.res').count()))
        p.screenshot(path=SHOTS + 'zoek-desktop.png')
        n_c = p.locator('#uit article.res [data-rzc=citaat]').count()
        n_l = p.locator('#uit article.res [data-rzc=link]').count()
        uitslag('a2 knoppen per treffer', n_c >= 5 and n_l >= 5, f'{n_c} citaat, {n_l} link')
        p.locator('#uit article.res [data-rzc=citaat]').first.click()
        p.wait_for_timeout(400)
        c = klembord(p)
        print('--- citaat (eerste treffer) ---\n' + c + '\n---')
        m = CIT_RE.match(c)
        uitslag('a3 klembord volgt formaat', bool(m))
        info = kaart_info(p, 0)
        uitslag('a4 citaat bevat het volledige segment (niet de ingekorte tekst)', bool(m) and schoon(info['fr']) in schoon(m['t']) and len(m['t']) >= len(info['fr'].strip('…')) - 2)
        uitslag('a5 spreker in citaat gelijk aan kaart', bool(m) and info['wie'].split(' (')[0] in c)
        uitslag('a6 toast zichtbaar', p.locator('.rz-toast, .rzc-toast').count() > 0 and 'Citaat gekopieerd' in p.locator('.rz-toast, .rzc-toast').last.inner_text())
        # selectie binnen het fragment: alleen die selectie
        p.evaluate("""()=>{const f=document.querySelector('#uit article.res .fr');const w=document.createTreeWalker(f,NodeFilter.SHOW_TEXT);
          let n=w.nextNode();while(n&&n.textContent.trim().length<30)n=w.nextNode();const r=document.createRange();r.setStart(n,5);r.setEnd(n,25);
          const s=getSelection();s.removeAllRanges();s.addRange(r);window.__sel=s.toString();}""")
        sel = p.evaluate('window.__sel')
        p.locator('#uit article.res [data-rzc=citaat]').first.click()
        p.wait_for_timeout(400)
        c2 = klembord(p)
        m2 = CIT_RE.match(c2)
        uitslag('a7 selectie binnen fragment: alleen die selectie', bool(m2) and schoon(sel) == schoon(m2['t']), repr(sel))
        # stuk-treffer
        p.close()
        # let op: voor 'parkeren' mist in deze checkout docs/data/tekst/b/697.zst (34 nieuwste stukken); daarom een andere zoekterm voor de stukken
        p = nieuwe_pagina(ctx, 'zoek.html#q=deelscooters&tab=stukken', 'zoek-stukken')
        p.wait_for_function("document.querySelectorAll('#uit article.res [data-rzc=verw]').length>0", timeout=60000)
        p.locator('#uit article.res [data-rzc=verw]').first.click()
        p.wait_for_timeout(400)
        v = klembord(p)
        print('--- verwijzing stuk ---\n' + v + '\n---')
        uitslag('a8 verwijzing stuk: Soort ‘titel’, wie, datum.\\nBron: url', bool(re.match(r"^[^\n‘]+ ‘.+’(, [^\n]+)?, \d{1,2} [a-z]+ \d{4}\.\nBron: https?://\S+$", v, re.S)))

        # ---------- (c) Copilot, beide tabs ----------
        p.get_by_role('tab', name=re.compile('Gezegd')).click()
        p.wait_for_function("document.querySelectorAll('#uit article.res [data-rzc=link]').length>0", timeout=30000)
        p.locator('#copbtn').click()
        p.wait_for_timeout(2500)
        cg = klembord(p)
        print('--- copilot gezegd (ingekort) ---\n' + cg[:900] + '\n[...]\n' + cg[-400:] + '\n---')
        copilot_check(cg, 'c1 gezegd', 12)
        p.get_by_role('tab', name=re.compile('Stukken')).click()
        p.wait_for_function("document.querySelectorAll('#uit article.res [data-rzc=verw]').length>0", timeout=30000)
        p.locator('#copbtn').click()
        p.wait_for_timeout(2500)
        cs = klembord(p)
        print('--- copilot stukken (ingekort) ---\n' + cs[:700] + '\n---')
        copilot_check(cs, 'c2 stukken', 10)
        # zonder treffers: knop verborgen
        p.evaluate("document.getElementById('q').value='xqzvwkjhg';document.getElementById('zf').requestSubmit()")
        p.wait_for_timeout(2500)
        uitslag('c3 knop verborgen zonder treffers', p.locator('#copbtn').is_hidden())
        p.close()

        # ---------- (b) vaste links ----------
        def link_test(naam, hash_, vereist=None):
            p = nieuwe_pagina(ctx, 'zoek.html#' + hash_, 'zoek-' + naam)
            wacht_treffers(p)
            kandidaat = None
            for i in range(min(p.locator('#uit article.res').count(), 15)):
                meta = p.locator('#uit article.res').nth(i).locator('.m').inner_text()
                if vereist is None or vereist(meta):
                    kandidaat = i
                    break
            if kandidaat is None:
                uitslag(f'b {naam}: geschikte treffer gevonden', False)
                p.close()
                return None
            a = p.locator('#uit article.res').nth(kandidaat)
            info = kaart_info(p, kandidaat)
            a.locator('[data-rzc=link]').click()
            p.wait_for_timeout(400)
            link = klembord(p)
            uitslag(f'b {naam}: link begint met https://raadzoeker.nl/zoek.html#b=', link.startswith('https://raadzoeker.nl/zoek.html#b='), link)
            a.locator('[data-rzc=citaat]').click()
            p.wait_for_timeout(300)
            cit = klembord(p)
            p.close()
            lokaal = link.replace('https://raadzoeker.nl/', BASE)
            q = nieuwe_pagina(ctx, lokaal[len(BASE):], 'fragment-' + naam)
            q.wait_for_selector('#frag', timeout=60000)
            kop = q.locator('#frag .fragkop h2').inner_text()
            ok_kaart = kop == 'Dit fragment'
            wie2 = q.locator('#frag .m b').inner_text()
            fr = schoon(q.locator('#frag .fragtekst').inner_text())
            mark = q.locator('#frag mark.fm')
            mark_txt = schoon(mark.inner_text()) if mark.count() else ''
            snip = schoon(info['fr'])
            uitslag(f'b {naam}: kaart "Dit fragment" met dezelfde spreker', ok_kaart and wie2 == info['wie'], f'{wie2!r} vs {info["wie"]!r}')
            uitslag(f'b {naam}: tekst van de treffer staat in de hele beurt', snip in fr, snip[:60])
            if 't=' in link:
                uitslag(f'b {naam}: segment gemarkeerd en bevat de treffer', bool(mark_txt) and snip in mark_txt)
            else:
                uitslag(f'b {naam}: (geen seconde in link, segment {"gemarkeerd" if mark_txt else "niet gemarkeerd"})', True)
            # citaat vanaf de fragmentkaart gelijk aan citaat uit de zoekresultaten (zelfde link)
            q.locator('#frag [data-rzc=link]').click()
            q.wait_for_timeout(400)
            link2 = klembord(q)
            uitslag(f'b {naam}: kaart geeft dezelfde link terug', link2 == link, link2)
            q.screenshot(path=SHOTS + f'fragmentlink-{naam}.png')
            if naam == 'raad2024':
                q.screenshot(path=SHOTS + 'fragmentlink.png')
            # hash blijft behouden en geen reload-lus
            h = q.evaluate('location.hash')
            q.wait_for_timeout(1500)
            uitslag(f'b {naam}: hash behoudt b na laden', 'b=' in h and q.evaluate('location.hash') == h)
            q.close()
            return cit

        link_test('commissie', 'q=parkeren&v=1', lambda m: m.startswith('Commissie'))
        link_test('raad2024', 'q=parkeren&v=0&van=2023&tot=2025', None)
        link_test('raad-voor-2022', 'q=parkeren&v=0&van=2018&tot=2021', lambda m: re.search(r'\b201[89]|\b202[01]\b', m) is not None)

        # niet gevonden
        q = nieuwe_pagina(ctx, 'zoek.html#b=9f0ee187~99999~niemand&t=5', 'niet-gevonden')
        q.wait_for_selector('#frag', timeout=60000)
        t = q.locator('#frag').inner_text()
        uitslag('b niet gevonden: nette melding + iBabs-link', 'niet meer te vinden' in t and q.locator('#frag a[href*="gemeenteraad.rotterdam.nl/Agenda/Index/9f0ee187"]').count() == 1, t[:80])
        q.close()

        # sleutels voor vergaderingen zonder agendaId (d<datum>r) en dubbele sleutels
        q = nieuwe_pagina(ctx, 'zoek.html', 'sleutels')
        q.wait_for_function("typeof DB!=='undefined'&&DB.M&&DB.M.u&&document.getElementById('van').options.length>0", timeout=60000)
        info = q.evaluate("""()=>{const L=[...keyIx().entries()];const d=L.find(([k])=>/^d\\d{8}[rc]~/.test(k));const dub=L.find(([k,v])=>v.length>1&&k.split('~')[1]!=='');
          return {d:d&&d[0],dub:dub&&dub[0],ndub:L.filter(([k,v])=>v.length>1).length,n:L.length};}""")
        print('sleutelindex:', info)
        q.close()
        if info['d']:
            q = nieuwe_pagina(ctx, 'zoek.html#b=' + info['d'].replace('~', '%7E') if False else 'zoek.html#b=' + info['d'], 'zonder-agendaid')
            q.wait_for_selector('#frag', timeout=60000)
            uitslag('b vergadering zonder agendaId (d<datum>r…): kaart gevonden', q.locator('#frag .fragtekst').count() == 1, info['d'])
            q.close()
        if info['dub']:
            q = nieuwe_pagina(ctx, 'zoek.html#b=' + info['dub'] + '&n=2', 'dubbele-sleutel')
            q.wait_for_selector('#frag', timeout=60000)
            uitslag('b dubbele sleutel met n=2: kaart gevonden', q.locator('#frag .fragtekst').count() == 1, info['dub'])
            q.close()

        # ---------- (d) dossiers ----------
        for slug, tag in (('parkeren', 'keten'), ('cameratoezicht', 'toon')):
            p = nieuwe_pagina(ctx, 'dossier.html#' + slug, 'dossier-' + slug)
            p.wait_for_selector('.kopacties [data-rzc=copilot]', timeout=60000)
            p.wait_for_timeout(500)
            p.locator('.kopacties [data-rzc=copilot]').click()
            p.wait_for_timeout(1500)
            c = klembord(p)
            print(f'--- copilot dossier {slug} ({len(c)} tekens, ingekort) ---\n' + c[:1500] + '\n[...]\n' + c[-300:] + '\n---')
            ok = len(c) <= 8000 and c.startswith('Je krijgt hieronder gegevens over het dossier') and 'Dossier: https://raadzoeker.nl/dossier.html?d=' + slug in c
            bronnen = [b for b in re.findall(r'^Bron: (\S+)', c, re.M) if b != 'Raadzoeker']
            ok2 = all(b.startswith('https://') for b in bronnen) and len(bronnen) >= 2
            uitslag(f'd {slug} ({tag}): Copilot-tekst ≤ 8000 en opbouw', ok and ok2, f'{len(c)} tekens, {len(bronnen)} bronnen')
            if slug == 'parkeren':
                p.screenshot(path=SHOTS + 'dossier.png')
            p.close()

        # ---------- (e) vergadering ----------
        idx = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'docs', 'verg', 'index.json')))
        vid = idx[0]['id']
        p = nieuwe_pagina(ctx, 'vergadering.html?id=' + vid, 'vergadering')
        p.wait_for_selector('.kort .zin', timeout=30000)
        p.locator('.kort .zin').first.click()
        p.wait_for_selector('#kcit [data-rzc=citaat]')
        p.locator('#kcit [data-rzc=citaat]').click()
        p.wait_for_timeout(400)
        c = klembord(p)
        print('--- citaat vergadering (kort) ---\n' + c + '\n---')
        uitslag('e1 vergadering (kort): citaat gekopieerd', c.startswith('‘') and 'Bron: https://gemeenteraad.rotterdam.nl/Agenda/Index/' in c and 'Fragment: https://raadzoeker.nl/vergadering.html?id=' + vid in c)
        p.locator('#kcit [data-rzc=link]').click()
        p.wait_for_timeout(300)
        uitslag('e2 vergadering: link is vergadering.html?id=…#ap-…', klembord(p).startswith('https://raadzoeker.nl/vergadering.html?id=' + vid + '#ap-'))
        p.locator('[data-m2=uitgebreid]').click()
        p.wait_for_selector('.ap .pt')
        p.locator('.ap .pt').first.click()
        p.wait_for_selector('.ap .pt .cit [data-rzc=citaat]')
        p.locator('.ap .pt .cit [data-rzc=citaat]').first.click()
        p.wait_for_timeout(400)
        c = klembord(p)
        uitslag('e3 vergadering (uitgebreid): citaat met fractie, agendapunt en ondertiteling', re.search(r'\n— [^,\n]+ \([^)]+\), gemeenteraad Rotterdam', c) is not None and 'agendapunt ' in c and 'automatische ondertiteling' in c, c.split('\n')[1] if '\n' in c else c)
        p.close()

        # ---------- ai-ballon (dossier met AI-samenvatting, geen keten) ----------
        p = nieuwe_pagina(ctx, 'dossier.html#cameratoezicht', 'ai-ballon')
        p.wait_for_selector('.z[data-c], .cl[data-c]', timeout=60000)
        p.locator('.z[data-c]:visible').first.click()
        p.wait_for_selector('#bub [data-rzc=citaat]')
        p.locator('#bub [data-rzc=citaat]').click()
        p.wait_for_timeout(400)
        c = klembord(p)
        print('--- citaat ai-ballon ---\n' + c + '\n---')
        uitslag('e4 AI-ballon: citaat met bron_label, datum en url', c.startswith('‘') and re.search(r'\n— .+, \d{1,2} [a-z]+ \d{4}', c) is not None and 'Bron: https://' in c and 'Fragment:' not in c)
        p.close()

        # ---------- terugval zonder Clipboard API (execCommand) ----------
        p = nieuwe_pagina(ctx, 'zoek.html#q=parkeren', 'terugval')
        wacht_treffers(p)
        p.evaluate("Object.defineProperty(navigator,'clipboard',{value:undefined,configurable:true});window.__kopie='';document.addEventListener('copy',e=>{window.__kopie=document.getSelection().toString();});")
        p.locator('#uit article.res [data-rzc=citaat]').first.click()
        p.wait_for_timeout(500)
        k = p.evaluate('window.__kopie')
        uitslag('h terugval zonder Clipboard API (execCommand) kopieert het citaat', k.startswith('‘') and 'Fragment: https://raadzoeker.nl/zoek.html#b=' in k)
        p.close()

        # ---------- (f) regressie: geen console-fouten ----------
        for url in ('', 'wijk.html', 'lab.html', 'zoek.html#q=parkeren', 'dossier.html#parkeren', 'dossier.html#cameratoezicht', 'vergadering.html?id=' + vid):
            p = nieuwe_pagina(ctx, url, 'regressie ' + url)
            p.wait_for_timeout(4000)
            p.close()

        # ---------- (g) mobiel ----------
        mob = br.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True, locale='nl-NL')
        mob.grant_permissions(['clipboard-read', 'clipboard-write'], origin='http://localhost:8771')
        mob.add_init_script(RUSTIG)
        p = nieuwe_pagina(mob, 'zoek.html#q=parkeren', 'zoek-mobiel')
        wacht_treffers(p)
        p.wait_for_selector('#copbtn:not([hidden])')
        p.wait_for_timeout(800)
        sw = p.evaluate('[document.documentElement.scrollWidth, window.innerWidth]')
        uitslag('g mobiel 390 px: geen horizontale scroll op zoek.html', sw[0] <= sw[1], str(sw))
        p.screenshot(path=SHOTS + 'zoek-mobiel.png')
        p.close()
        br.close()

    # console-fouten
    print('\n=== console- en paginafouten ===')
    echt = []
    for naam, soort, tekst in FOUTEN:
        negeer = ('/api/' in tekst) or ('501' in tekst and 'POST' in tekst) or ('Failed to load resource' in tekst and '404' in tekst) or ('sdk.companywebcast' in tekst)
        print(('  (genegeerd) ' if negeer else '  ') + f'[{naam}] {soort}: {tekst[:200]}')
        if not negeer:
            echt.append((naam, tekst))
    uitslag('f geen console- of paginafouten (zonder /api/ en 404 op externe bronnen)', not echt, str(echt[:3]))

    print('\n=== samenvatting ===')
    fout = [n for n, ok in RES if not ok]
    print(f'{len(RES) - len(fout)} van {len(RES)} controles geslaagd')
    for n in fout:
        print('  FOUT:', n)
    sys.exit(1 if fout else 0)


def copilot_check(c, naam, maxn):
    uitslag(f'{naam}: lengte ≤ 8000', len(c) <= 8000, str(len(c)))
    nums = re.findall(r'^\[(\d+)\] ', c, re.M)
    uitslag(f'{naam}: genummerde fragmenten 1..N', nums == [str(i) for i in range(1, len(nums) + 1)] and 1 <= len(nums) <= maxn, str(len(nums)))
    bronnen = [b for b in re.findall(r'^Bron: (\S+)', c, re.M) if b != 'Raadzoeker']
    uitslag(f'{naam}: elke bronlink begint met https://', bool(bronnen) and all(b.startswith('https://') for b in bronnen), f'{len(bronnen)} links')
    uitslag(f'{naam}: opdracht bovenaan en voetregel', c.startswith('Je krijgt hieronder letterlijke fragmenten uit') and re.search(r'Bron: Raadzoeker \(raadzoeker\.nl\), onofficieel hulpmiddel op basis van openbare raadsinformatie\. \d+ van \d+ fragmenten\. Zoekopdracht: https://raadzoeker\.nl/zoek\.html#', c) is not None)


if __name__ == '__main__':
    main()
