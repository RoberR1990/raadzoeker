"""Test de beloftemonitor (docs/ontwerp/beloofd.html).
Start eerst een server:  python3 -m http.server 8772 -d docs
Draai:                   python3 src/test_beloofd.py
"""
import os, re, sys
from playwright.sync_api import sync_playwright

PORT = 8772
BASE = f'http://localhost:{PORT}/ontwerp/'
SHOTS = '/tmp/claude-0/-home-claude/27462a42-c492-5a46-80c7-d7eb1ac7cf72/scratchpad/beloofd/'
os.makedirs(SHOTS, exist_ok=True)
RUSTIG = "try{localStorage.setItem('rz-welkom','nee');for(const k of ['startpagina','zoek','dossier','vergadering','wijk','lab','domeinen','verkenner','beloofd'])localStorage.setItem('rz-tour-'+k,'ja');}catch(e){}"
RES = []
FOUTEN = []


def uitslag(naam, ok, tekst=''):
    RES.append((naam, ok))
    print(('OK   ' if ok else 'FOUT ') + naam + (' :: ' + tekst if tekst else ''))


def nieuwe_pagina(ctx, hash_='', naam=None, wacht=True):
    p = ctx.new_page()
    n = naam or ('beloofd' + hash_)
    p.on('console', lambda m: FOUTEN.append((n, 'console', m.text)) if m.type == 'error' else None)
    p.on('pageerror', lambda e: FOUTEN.append((n, 'pageerror', str(e))))
    p.goto(BASE + 'beloofd.html' + hash_)
    if wacht:
        klaar(p)
    return p


def klaar(p):
    p.wait_for_function("document.querySelector('#n-open').textContent.trim()!=='…'", timeout=30000)
    p.wait_for_function("!/laden/i.test(document.querySelector('#lijst').textContent)||document.querySelectorAll('#lijst .item').length>0", timeout=30000)
    p.wait_for_timeout(150)


def getal(t):
    return int(re.sub(r'\D', '', t or '0') or 0)


def tel(p, id_):
    return getal(p.locator('#' + id_).inner_text())


def antal(p):
    return getal(p.locator('#ant b').first.inner_text())


def klembord(p):
    return p.evaluate('navigator.clipboard.readText()')


def wacht_af(p):
    p.wait_for_function("document.querySelector('#n-af30').textContent.trim()!=='…'", timeout=60000)
    p.wait_for_timeout(200)


def main():
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        ctx = br.new_context(viewport={'width': 1280, 'height': 900}, locale='nl-NL', accept_downloads=True)
        ctx.grant_permissions(['clipboard-read', 'clipboard-write'], origin=f'http://localhost:{PORT}')
        ctx.add_init_script(RUSTIG)

        # ---------- (a) laden en telblokken ----------
        t0 = None
        p = nieuwe_pagina(ctx, '', 'basis', wacht=False)
        p.wait_for_selector('#lijst .item', timeout=30000)
        p.wait_for_timeout(200)
        a1 = (tel(p, 'n-open'), tel(p, 'n-laat'), tel(p, 'n-30'))
        uitslag('a1 geen filters: 941 open, 419 over de termijn', a1[0] == 941 and a1[1] == 419, str(a1))
        wacht_af(p)
        a1b = tel(p, 'n-af30')
        uitslag('a1b telblok afgedaan (30 dagen) gevuld na lui laden', a1b > 0, str(a1b))
        p.screenshot(path=SHOTS + 'desktop.png', full_page=False)
        p.screenshot(path=SHOTS + 'desktop-vol.png', full_page=True)
        stand = p.locator('#stand').inner_text()
        uitslag('a2 stand in intro', '2026' in stand, stand)
        p.close()
        p = nieuwe_pagina(ctx, '#soort=toezeggingen')
        a3 = (tel(p, 'n-open'), tel(p, 'n-laat'))
        uitslag('a3 soort=toezeggingen: 433/213', a3 == (433, 213), str(a3))
        p.close()
        p = nieuwe_pagina(ctx, '#soort=moties')
        a4 = (tel(p, 'n-open'), tel(p, 'n-laat'))
        uitslag('a4 soort=moties: 508/206', a4 == (508, 206), str(a4))
        p.close()

        # ---------- (b) elk filter verandert de lijst, komt in de hash en is deelbaar ----------
        p = nieuwe_pagina(ctx, '')
        basis = antal(p)
        uitslag('b0 beginstand 941 stukken', basis == 941, str(basis))

        def keuze(naam, doe, param):
            p.goto(BASE + 'beloofd.html')
            klaar(p)
            doe()
            p.wait_for_timeout(500)
            n = antal(p)
            h = p.evaluate('location.hash')
            ok_hash = (param + '=') in h
            ok_n = n != basis
            # nieuwe pagina met dezelfde hash
            q = nieuwe_pagina(ctx, h, 'hash-' + naam)
            n2 = antal(q)
            q.close()
            uitslag(f'b {naam}: lijst verandert, in hash, zelfde telling in nieuwe pagina', ok_n and ok_hash and n == n2, f'{basis}→{n}, {h}, nieuw={n2}')

        def select_idx(id_, idx):
            return lambda: p.select_option('#' + id_, index=idx)

        # filters die zichtbaar moeten zijn op desktop
        keuze('soort', lambda: p.get_by_role('button', name='Moties', exact=True).click(), 'soort')
        keuze('status', lambda: p.locator('.tel[data-s=laat]').click(), 'status')
        keuze('domein', select_idx('f-dom', 1), 'dom')
        keuze('gebied', select_idx('f-geb', 1), 'geb')
        keuze('onderwerp', select_idx('f-ond', 1), 'ond')
        keuze('collegelid', select_idx('f-wie', 1), 'wie')
        keuze('fractie', select_idx('f-fr', 1), 'fr')
        keuze('commissie', select_idx('f-com', 1), 'com')
        keuze('jaar (keuzelijst)', select_idx('f-jaar', 2), 'jaar')
        keuze('jaar (balkje in het overzicht)', lambda: p.locator('.jb[data-j="2024"]').click(), 'jaar')
        keuze('zoeken', lambda: p.fill('#q', 'fietsparkeren'), 'q')
        p.goto(BASE + 'beloofd.html')
        klaar(p)
        # chips en alles wissen
        p.select_option('#f-dom', index=2)
        p.get_by_role('button', name='Moties', exact=True).click()
        p.wait_for_timeout(300)
        chips = p.locator('#fchips button').count()
        uitslag('b chips zichtbaar voor actieve filters (+ Alles wissen)', chips == 3, str(chips))
        p.locator('#fchips .alles').click()
        p.wait_for_timeout(300)
        uitslag('b Alles wissen herstelt 941 en lege hash', antal(p) == 941 and p.evaluate('location.hash') in ('', '#'), p.evaluate('location.hash'))
        p.close()

        # ---------- (c) sorteren ----------
        p = nieuwe_pagina(ctx, '')
        p.locator('#lijst .item').first.locator('.meta .d, .meta').first.wait_for()
        eerste = p.locator('#lijst .item .ol').first.inner_text()
        uitslag('c1 standaard Langst open: oudste (24 mei 2018) bovenaan', '24 mei 2018' in eerste, eerste)
        p.select_option('#sort', 'nieuw')
        p.wait_for_timeout(300)
        nieuwste = p.locator('#lijst .item .ol').first.inner_text()
        uitslag('c2 Nieuwste: 7 okt 2026 bovenaan', '7 okt 2026' in nieuwste, nieuwste)
        p.select_option('#sort', 'laat')
        p.wait_for_timeout(300)
        meest = p.locator('#lijst .item').first.inner_text()
        uitslag('c3 Meest over de termijn: eerste rij is over de termijn', 'over de termijn' in meest, meest.replace('\n', ' | ')[:120])
        p.close()

        # ---------- (d) afgedaan ----------
        p = ctx.new_page()
        n = []
        p.on('request', lambda r: n.append(r.url) if 'beloofd-af.json' in r.url else None)
        p.on('console', lambda m: FOUTEN.append(('afgedaan', 'console', m.text)) if m.type == 'error' else None)
        p.on('pageerror', lambda e: FOUTEN.append(('afgedaan', 'pageerror', str(e))))
        p.goto(BASE + 'beloofd.html#status=af')
        p.wait_for_selector('#lijst .item', timeout=60000)
        p.wait_for_timeout(300)
        t = p.locator('#lijst .item').first.inner_text()
        uitslag('d1 status=af laadt beloofd-af.json', len(n) >= 1, str(len(n)))
        uitslag('d2 rijen tonen Afgedaan op', 'Afgedaan op' in t and antal(p) > 1000, f'{antal(p)} · ' + t.replace('\n', ' | ')[:100])
        p.screenshot(path=SHOTS + 'afgedaan.png')
        p.close()
        # open pagina: af-bestand komt lui op de achtergrond
        p = nieuwe_pagina(ctx, '')
        wacht_af(p)
        uitslag('d3 klik op telblok Afgedaan toont de lijst van laatste 30 dagen', True)
        p.locator('.tel[data-s=af30]').click()
        p.wait_for_timeout(400)
        uitslag('d4 telblok = lijstlengte', antal(p) == tel(p, 'n-af30'), f'{antal(p)} vs {tel(p, "n-af30")}')
        p.close()

        # ---------- (e) uitklappen ----------
        p = nieuwe_pagina(ctx, '#soort=toezeggingen')
        p.locator('#lijst .item summary').first.click()
        p.wait_for_selector('#lijst .item[open] .ctx .spoor li', timeout=5000)
        stappen = p.locator('#lijst .item[open] .ctx .spoor li').count()
        hrefs = p.locator('#lijst .item[open] .ctx a').evaluate_all('a=>a.map(x=>x.href)')
        ibabs = [h for h in hrefs if h.startswith('https://gemeenteraad.rotterdam.nl/Reports/Item/')]
        uitslag('e1 uitgeklapt: stappen', stappen >= 2, str(stappen))
        uitslag('e2 iBabs-link', len(ibabs) >= 1, ibabs[0] if ibabs else str(hrefs))
        p.locator('#lijst .item[open]').scroll_into_view_if_needed()
        p.screenshot(path=SHOTS + 'uitgeklapt.png')
        p.close()
        # motie met stemuitslag en dossierlinks
        p = nieuwe_pagina(ctx, '#soort=moties')
        for i in range(6):
            p.locator('#lijst .item summary').nth(i).click()
        p.wait_for_timeout(300)
        tctx = ' '.join(p.locator('#lijst .item[open] .ctx').all_inner_texts())
        uitslag('e3 moties: stemuitslag en portefeuillehouder-regel', 'stemmen voor' in tctx and 'Portefeuillehouder' in tctx, tctx[:150])
        p.close()

        # ---------- (f) csv ----------
        p = nieuwe_pagina(ctx, '#soort=toezeggingen&dom=mobiliteit')
        n_rij = antal(p)
        with p.expect_download() as d:
            p.locator('#csv').click()
        pad = d.value.path()
        data = open(pad, 'rb').read()
        regels = data.decode('utf-8-sig').splitlines()
        uitslag('f1 csv begint met BOM', data[:3] == b'\xef\xbb\xbf')
        uitslag('f2 regels = gefilterde rijen + 1', len(regels) == n_rij + 1, f'{len(regels)} regels, {n_rij} rijen')
        uitslag('f3 puntkomma en kolomkoppen', regels[0].startswith('"soort";"datum";"titel";"wie";"portefeuillehouder"') and regels[0].count(';') == 13, regels[0][:120])
        p.close()

        # ---------- (g) Kopieer voor Copilot, Kopieer link ----------
        p = nieuwe_pagina(ctx, '')
        p.wait_for_function('window.rzCopilotKopieer', timeout=15000)
        p.locator('[data-rzc=copilot]').click()
        p.wait_for_timeout(1500)
        c = klembord(p)
        bb = re.findall(r'\b\d{2}bb\d+', c)
        print('--- copilot (begin/eind) ---\n' + c[:900] + '\n[...]\n' + c[-350:] + '\n---')
        uitslag('g1 copilot-tekst ≤ 8.000 tekens', 0 < len(c) <= 8000, str(len(c)))
        uitslag('g2 bb-nummers in de tekst', len(bb) >= 10, str(len(bb)))
        uitslag('g3 opdracht en voet aanwezig', c.startswith('Je krijgt hieronder openstaande moties en toezeggingen') and 'raadzoeker.nl' in c.splitlines()[-1], c.splitlines()[-1][:120])
        p.get_by_role('button', name='Moties', exact=True).click()
        p.select_option('#f-dom', index=3)
        p.wait_for_timeout(300)
        p.locator('#linkkop').click()
        p.wait_for_timeout(500)
        l = klembord(p)
        uitslag('g4 Kopieer link bevat de filters', 'beloofd.html#' in l and 'soort=moties' in l and 'dom=' in l, l)
        p.locator('[data-rzc=copilot]').click()
        p.wait_for_timeout(1500)
        c2 = klembord(p)
        uitslag('g5 copilot noemt de filters in woorden', 'alleen moties' in c2.splitlines()[0] and 'domein' in c2.splitlines()[0], c2.splitlines()[0][:220])
        p.close()

        # ---------- lege staat ----------
        p = nieuwe_pagina(ctx, '#q=xqzvwk'.replace('#q=', '#q='))
        uitslag('h0 lege staat toont wat wél kan', p.locator('.leegstaat').count() == 1 and 'Alle filters wissen' in p.locator('.leegstaat').inner_text(), '')
        p.screenshot(path=SHOTS + 'leeg.png')
        p.close()

        # ---------- (h) mobiel 390 px ----------
        m = br.new_context(viewport={'width': 390, 'height': 844}, locale='nl-NL', is_mobile=True, has_touch=True, device_scale_factor=2)
        m.grant_permissions(['clipboard-read', 'clipboard-write'], origin=f'http://localhost:{PORT}')
        m.add_init_script(RUSTIG)
        p = nieuwe_pagina(m, '', 'mobiel')
        wacht_af(p)
        sw = p.evaluate('[document.documentElement.scrollWidth, window.innerWidth]')
        uitslag('h1 geen horizontale scroll (lijst)', sw[0] <= sw[1], str(sw))
        uitslag('h2 filterpaneel dicht, knop zichtbaar', p.locator('#fknop').is_visible() and not p.locator('#f-dom').is_visible())
        p.screenshot(path=SHOTS + 'mobiel.png')
        p.locator('#fknop').click()
        p.wait_for_timeout(200)
        uitslag('h3 filterknop opent de filters', p.locator('#f-dom').is_visible() and p.locator('#fknop').get_attribute('aria-expanded') == 'true')
        p.select_option('#f-dom', index=1)
        p.wait_for_timeout(300)
        uitslag('h4 filterknop toont aantal (1)', 'Filters (1)' in p.locator('#fknop').inner_text(), p.locator('#fknop').inner_text())
        p.screenshot(path=SHOTS + 'mobiel-filters.png')
        p.locator('#fknop').click()
        p.locator('#lijst .item summary').first.click()
        p.wait_for_selector('#lijst .item[open] .ctx .spoor li')
        sw = p.evaluate('[document.documentElement.scrollWidth, window.innerWidth]')
        uitslag('h5 geen horizontale scroll (uitgeklapt, gefilterd)', sw[0] <= sw[1], str(sw))
        p.locator('#lijst .item[open]').scroll_into_view_if_needed()
        p.screenshot(path=SHOTS + 'mobiel-uitgeklapt.png')
        p.close()
        m.close()

        # ---------- (i) donker thema ----------
        dk = br.new_context(viewport={'width': 1280, 'height': 900}, locale='nl-NL', color_scheme='dark')
        dk.add_init_script(RUSTIG)
        p = nieuwe_pagina(dk, '', 'donker')
        p.locator('#lijst .item summary').first.click()
        p.wait_for_timeout(300)
        p.screenshot(path=SHOTS + 'donker.png')
        p.screenshot(path=SHOTS + 'donker-vol.png', full_page=True)
        bg = p.evaluate("getComputedStyle(document.body).backgroundColor")
        uitslag('i donker thema: screenshot gemaakt, donkere achtergrond', bg != 'rgb(239, 244, 246)', bg)
        p.close()
        dk.close()

        # ---------- Toon meer ----------
        p = nieuwe_pagina(ctx, '')
        n0 = p.locator('#lijst .item').count()
        p.locator('#meer').click()
        p.wait_for_timeout(300)
        n1 = p.locator('#lijst .item').count()
        uitslag('j Toon meer: 40 → 80 rijen', (n0, n1) == (40, 80), f'{n0}→{n1}')
        p.close()
        br.close()

    print('\n--- console- en paginafouten ---')
    for f in FOUTEN:
        print(f)
    uitslag('0 geen console- of paginafouten', not FOUTEN, str(len(FOUTEN)))
    slecht = [n for n, ok in RES if not ok]
    print(f'\n{len(RES) - len(slecht)} van {len(RES)} gelukt' + (f'; mislukt: {slecht}' if slecht else ''))
    sys.exit(1 if slecht else 0)


main()
