"""Test dossiertijdlijn (docs/lijn.js).
Start eerst een server:  python3 -m http.server 8773 -d docs
Draai:                   python3 src/test_lijn.py
"""
import json, os, re, sys
from playwright.sync_api import sync_playwright

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs')
BASE = 'http://localhost:8773/'
SHOTS = '/tmp/claude-0/-home-claude/27462a42-c492-5a46-80c7-d7eb1ac7cf72/scratchpad/lijn/'
os.makedirs(SHOTS, exist_ok=True)
RUSTIG = "try{localStorage.setItem('rz-welkom','nee');for(const k of ['startpagina','zoek','dossier','vergadering','wijk','lab','domeinen','verkenner'])localStorage.setItem('rz-tour-'+k,'ja');}catch(e){}"
RES, FOUTEN = [], []


def uitslag(naam, ok, tekst=''):
    RES.append((naam, ok))
    print(('OK   ' if ok else 'FOUT ') + naam + (' :: ' + tekst if tekst else ''))


def jl(p):
    return json.load(open(os.path.join(ROOT, p), encoding='utf8'))


def pagina(ctx, url, naam=None):
    p = ctx.new_page()
    p.on('console', lambda m: FOUTEN.append((naam or url, 'console', m.text)) if m.type == 'error' else None)
    p.on('pageerror', lambda e: FOUTEN.append((naam or url, 'pageerror', str(e))))
    p.goto(BASE + url)
    return p


def laad_lijn(p, open_=False):
    """wacht tot de tijdlijn getekend is; open_ klapt hem open"""
    p.wait_for_selector('.lijnhost', state='attached', timeout=30000)
    p.locator('.lijnhost').first.scroll_into_view_if_needed()
    p.wait_for_selector('.lijnbox .lj-strook', timeout=30000)
    if open_ and not p.locator('.lj-jaren').count():
        p.locator('#k-tijdlijn .kkop, [data-tg]').first.click()
        p.wait_for_selector('.lj-jaren', timeout=15000)


def n(p, sel):
    return p.locator(sel).count()


def chip_aantal(p, g):
    t = p.locator(f'[data-fc="{g}"] .n').first.inner_text()
    return int(re.sub(r'\D', '', t))


def alle_jaren(p):
    while p.locator('.lj-jb:not(.on)').count():
        p.locator('.lj-jb:not(.on)').first.click()


def tijd(p, js_sel, wacht):
    """tijd tot de volgende getekende frame na een klik"""
    return p.evaluate("""async s=>{const b=document.querySelector(s);const t=performance.now();b.click();
      await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));return performance.now()-t;}""", js_sel)


def main():
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        ctx = br.new_context(viewport={'width': 1280, 'height': 900}, locale='nl-NL')
        ctx.add_init_script(RUSTIG)

        # ---------- (a) parkeren ----------
        j = jl('lijn/parkeren.json')
        tel = j['tel']
        nb = sum(1 for e in j['e'] if e[1] == 'besluit')
        p = pagina(ctx, 'dossier.html#parkeren', 'dossier-parkeren')
        laad_lijn(p)
        uitslag('a1 blok Tijdlijn bestaat (dicht: strook + 3 nieuwste)', n(p, '#k-tijdlijn') == 1 and n(p, '#k-tijdlijn .lj-pre .lj-e') == 3 and n(p, '#k-tijdlijn .lj-sj') >= 5)
        p.screenshot(path=SHOTS + 'parkeren-dicht.png')
        t_open = tijd(p, '#k-tijdlijn .kkop', 0)
        p.wait_for_selector('.lj-jaren', timeout=15000)
        p.wait_for_timeout(300)
        uitslag('a2 open: gebeurtenissen aan beide kanten', n(p, '.lj-jaren .lj-e.r') > 3 and n(p, '.lj-jaren .lj-e.c') > 3, f"raad {n(p, '.lj-jaren .lj-e.r')}, college {n(p, '.lj-jaren .lj-e.c')}")
        uitslag('a3 link wordt #parkeren/tijdlijn', p.evaluate('location.hash') == '#parkeren/tijdlijn', p.evaluate('location.hash'))
        gem = {'debat': chip_aantal(p, 'debat'), 'motie': chip_aantal(p, 'motie'), 'toez': chip_aantal(p, 'toez'), 'brief': chip_aantal(p, 'brief'),
               'vragen': chip_aantal(p, 'vragen'), 'voorstel': chip_aantal(p, 'voorstel'), 'wijk': chip_aantal(p, 'wijk')}
        verw = {'debat': tel['debat'], 'motie': tel['motie'], 'toez': tel['toez'], 'brief': tel['brief'] - nb, 'vragen': tel['vragen'], 'voorstel': tel['voorstel'] + nb, 'wijk': tel['wijk']}
        uitslag('a4 aantallen op de chips kloppen met tel (brieven en besluiten: tel.brief telt besluiten mee, de chip Voorstellen en besluiten ook)', gem == verw, f'{gem} tegenover {verw}')
        uitslag('a5 chip Alles = aantal gebeurtenissen', chip_aantal(p, 'alles') if False else int(re.sub(r'\D', '', p.locator('[data-fa] .n').first.inner_text())) == len(j['e']))
        p.locator('.lj-jaren').scroll_into_view_if_needed()
        p.screenshot(path=SHOTS + 'parkeren-open.png')
        p.locator('#k-tijdlijn').screenshot(path=SHOTS + 'parkeren-blok.png')

        # ---------- (b) filters ----------
        brieven_vis = n(p, '.lj-e.t-brief')
        uitslag('b1 brieven staan standaard uit (alleen afdoeningsvoorstellen)', brieven_vis < tel['brief'] // 3 and 'verborgen' in p.locator('.lj-hint').inner_text(), f'{brieven_vis} zichtbaar; {p.locator(".lj-hint").inner_text()[:60]}')
        p.locator('[data-fb]').click()
        alle_jaren(p)
        p.wait_for_timeout(200)
        uitslag("b2 'toon' zet brieven aan", n(p, '.lj-e.t-brief') > brieven_vis and 'Alle' in p.locator('.lj-hint').inner_text(), f'{n(p, ".lj-e.t-brief")} brieven')
        p.locator('[data-fc="motie"]').click()
        p.wait_for_timeout(200)
        tot, mo = n(p, '.lj-jaren .lj-e'), n(p, '.lj-jaren .lj-e.t-motie, .lj-jaren .lj-e.t-amendement')
        uitslag('b3 filter Moties toont alleen moties/amendementen', tot > 0 and tot == mo, f'{mo} van {tot}')
        p.locator('[data-fa]').click()
        p.locator('[data-fo]').click()
        p.wait_for_timeout(200)
        tot, op = n(p, '.lj-jaren .lj-e'), n(p, '.lj-jaren .lj-e.opn')
        verwacht_open = sum(1 for e in j['e'] if isinstance(e[6], dict) and e[6].get('st') == 4)
        uitslag("b4 'Alleen wat nog openstaat' toont alleen st 4", tot > 0 and tot == op, f'{op} van {tot}; bestand heeft {verwacht_open} open (sommige in ingeklapte jaren)')
        p.locator('[data-fo]').click()
        p.locator('[data-fa]').click()

        # ---------- (c) oudere jaren ----------
        p.locator('[data-fc="debat"]').click()
        p.locator('[data-fa]').click()
        while n(p, '.lj-jb.on') > 1:
            p.locator('.lj-jb.on').last.click()
        voor = n(p, '.lj-jaren .lj-e')
        dicht = p.locator('.lj-jb:not(.on)')
        jaar = dicht.first.get_attribute('data-jk')
        dicht.first.click()
        p.wait_for_timeout(200)
        uitslag(f'c1 ouder jaar ({jaar}) openklappen voegt gebeurtenissen toe', n(p, '.lj-jaren .lj-e') > voor, f'{voor} -> {n(p, ".lj-jaren .lj-e")}')
        p.evaluate('window.scrollTo(0,0)')
        p.locator('[data-jr="2019"]').click()
        p.wait_for_timeout(1200)
        r = p.evaluate("(()=>{const e=document.getElementById('lj-parkeren-2019');const r=e.getBoundingClientRect();return [r.top,innerHeight,!!e.querySelector('.lj-ev')]})()")
        uitslag('c2 jaarstrook springt naar 2019 (in beeld en open)', r[2] and -10 < r[0] < r[1], str(r))

        # ---------- (d) spoor ----------
        p.locator('[data-fa]').click()
        p.locator('[data-fc="toez"]').click()
        p.wait_for_timeout(200)
        p.locator('.lj-e.opn [data-ld]').first.scroll_into_view_if_needed()
        p.locator('.lj-e.opn [data-ld]').first.click()
        p.wait_for_selector('.lj-d .spoor li')
        stappen = n(p, '.lj-d .spoor li')
        links = p.locator('.lj-d a[href*="gemeenteraad.rotterdam.nl"]').count()
        uitslag('d1 spoor met stappen en link naar gemeenteraad.rotterdam.nl', stappen >= 2 and links >= 1, f'{stappen} stappen, {links} links')
        uitslag('d2 statusstip met woorden', re.search(r'Afdoening verwacht|dagen over de termijn|Open', p.locator('.lj-d .lj-st').first.inner_text()) is not None, p.locator('.lj-d .lj-st').first.inner_text())
        # een afgedane motie met bijbehorende brief: gemarkeerde gebeurtenissen
        p.locator('[data-fa]').click()
        p.locator('[data-fc="motie"]').click()
        p.wait_for_timeout(200)
        alle_jaren(p)
        p.wait_for_timeout(200)
        p.locator('.lj-e.t-motie:not(.opn) [data-ld]').nth(3).scroll_into_view_if_needed()
        p.locator('.lj-e.t-motie:not(.opn) [data-ld]').nth(3).click()
        p.wait_for_timeout(300)
        uitslag('d3 bijbehorende gebeurtenissen lichten op', n(p, '.lj-e.hf') == 1, f"{n(p, '.lj-e.dr')} gemarkeerd")
        p.locator('.lj-e.hf').scroll_into_view_if_needed()
        p.screenshot(path=SHOTS + 'parkeren-spoor.png')

        # ---------- (e) video ----------
        p.locator('[data-fa]').click()
        p.locator('[data-fc="debat"]').click()
        p.wait_for_timeout(200)
        p.locator('[data-lv]').first.scroll_into_view_if_needed()
        p.locator('[data-lv]').first.click()
        p.wait_for_selector('#kvid:not([hidden])', timeout=10000)
        uitslag('e1 ▶ Bekijk opent het videovenster', p.locator('#kvid').is_visible())
        p.screenshot(path=SHOTS + 'video.png')
        p.locator('#kvx').click()
        uitslag('e2 videovenster sluit', p.locator('#kvid').is_hidden())

        # ---------- (i) tijden ----------
        p.close()
        p = pagina(ctx, 'dossier.html#parkeren', 'dossier-parkeren-2')
        laad_lijn(p)
        t1 = tijd(p, '#k-tijdlijn .kkop', 0)
        p.wait_for_selector('.lj-jaren')
        t2 = tijd(p, '[data-fc="motie"]', 0)
        t3 = tijd(p, '[data-fa]', 0)
        uitslag('i1 openklappen < 300 ms', t1 < 300, f'{t1:.0f} ms')
        uitslag('i2 één filterwissel < 300 ms', t2 < 300 and t3 < 300, f'{t2:.0f} ms en terug {t3:.0f} ms')
        # 1.500 gebeurtenissen: alles aan, alle jaren open
        alle_jaren(p)
        t4 = tijd(p, '[data-fc="debat"]', 0)
        uitslag('i3 filterwissel met alle jaren open < 300 ms', t4 < 300, f'{t4:.0f} ms, {n(p, ".lj-e")} kaarten')

        # ---------- (l) regressie bestaande blokken ----------
        p.locator('#k-gezegd .kkop').click()
        p.wait_for_timeout(300)
        uitslag('l1 ander blok (Gezegd) opent nog; tijdlijn blijft werken', p.locator('#k-gezegd').evaluate("e=>e.classList.contains('open')") and n(p, '.lj-jaren') == 1)
        p.close()

        # ---------- (f) andere dossiers ----------
        p = pagina(ctx, 'dossier.html#cameratoezicht', 'cameratoezicht')
        laad_lijn(p)
        uitslag('f1 dossier zonder extra: sectie Tijdlijn onder de kop', p.locator('#lijnsec h2').inner_text() == 'Tijdlijn' and p.locator('#lijnsec').is_visible())
        p.locator('[data-tg]').click()
        p.wait_for_selector('.lj-jaren')
        uitslag('f2 openklappen zet #cameratoezicht/tijdlijn', p.evaluate('location.hash') == '#cameratoezicht/tijdlijn' and n(p, '.lj-e.r') > 0 and n(p, '.lj-e.c') > 0)
        p.screenshot(path=SHOTS + 'cameratoezicht-open.png', full_page=False)
        p.close()
        p = pagina(ctx, 'dossier.html#cameratoezicht/tijdlijn', 'cameratoezicht-hash')
        p.wait_for_selector('.lj-jaren', timeout=20000)
        uitslag('f3 #slug/tijdlijn opent direct', n(p, '.lj-jaren') == 1)
        p.close()
        for slug in ['mobiliteit', 'wonen-en-bouwen--feijenoord' if os.path.exists(ROOT + '/lijn/wonen-en-bouwen--feijenoord.json') else None]:
            if not slug:
                continue
            jj = jl(f'lijn/{slug}.json')
            p = pagina(ctx, f'dossier.html#{slug}', slug)
            laad_lijn(p)
            p.locator('[data-tg], #k-tijdlijn .kkop').first.click()
            p.wait_for_selector('.lj-jaren')
            afk = p.locator('.lj-afk').count()
            uitslag(f'f4 {slug}: tijdlijn werkt' + (' en afgekapt-regel staat erbij' if jj.get('afgekapt') else ''), n(p, '.lj-e') > 0 and (afk == 1) == bool(jj.get('afgekapt')),
                    f"afgekapt={jj.get('afgekapt')}, regel: {p.locator('.lj-afk').first.inner_text() if afk else '-'}")
            if slug == 'mobiliteit':
                p.screenshot(path=SHOTS + 'mobiliteit.png')
            p.close()
        kr = [s for s in jl('d/index.json')['d'] if s['soort'] == 'kruising' and os.path.exists(f"{ROOT}/lijn/{s['slug']}.json")]
        afk_kr = [s for s in kr if jl(f"lijn/{s['slug']}.json").get('afgekapt')]
        for s in ([afk_kr[0]] if afk_kr else []) + [kr[0]]:
            p = pagina(ctx, f"dossier.html#{s['slug']}", s['slug'])
            laad_lijn(p)
            p.locator('[data-tg]').click()
            p.wait_for_selector('.lj-jaren')
            uitslag(f"f5 kruising {s['slug']} werkt", n(p, '.lj-e') > 0, f"afgekapt-regel: {n(p, '.lj-afk')}")
            p.close()

        # ---------- (h) zonder lijn-bestand ----------
        ix = jl('lijn/index.json')
        mist = [s['slug'] for s in jl('d/index.json')['d'] if s['slug'] not in ix]
        print('   ontbrekend:', mist)
        for slug in mist[:2]:
            p = pagina(ctx, f'dossier.html#{slug}', 'mist-' + slug)
            p.wait_for_selector('#dossier h1', timeout=20000)
            p.wait_for_timeout(1200)
            uitslag(f'h {slug}: geen blok, geen fout', n(p, '.lijnbox .lj-strook') == 0 and not p.locator('#lijnsec').is_visible())
            p.close()

        # ---------- (g) wijk.html ----------
        p = pagina(ctx, 'wijk.html#delfshaven', 'wijk-delfshaven')
        laad_lijn(p)
        p.locator('[data-tg]').click()
        p.wait_for_selector('.lj-jaren')
        uitslag('g1 gebied: tijdlijn werkt aan beide kanten', n(p, '.lj-e.r') > 0 and n(p, '.lj-e.c') > 0)
        uitslag('g2 link #delfshaven/tijdlijn', p.evaluate('location.hash') == '#delfshaven/tijdlijn')
        # video op wijk.html: keten.js wordt pas bij ▶ geladen
        had = p.evaluate("typeof kVideo")
        p.locator('[data-fc="debat"]').click()
        p.locator('[data-lv]').first.scroll_into_view_if_needed()
        p.locator('[data-lv]').first.click()
        p.wait_for_selector('#kvid:not([hidden])', timeout=15000)
        uitslag('g3 ▶ op wijk.html laadt keten.js en opent het venster', had == 'undefined' and p.locator('#kvid').is_visible(), f'kVideo vooraf: {had}')
        p.locator('#kvx').click()
        p.locator('[data-fa]').click()
        p.locator('#tl').scroll_into_view_if_needed()
        p.screenshot(path=SHOTS + 'gebied-delfshaven.png')
        p.close()
        p = pagina(ctx, 'wijk.html#delfshaven/tijdlijn', 'wijk-hash')
        p.wait_for_selector('.lj-jaren', timeout=20000)
        uitslag('g4 #gebied/tijdlijn opent direct', n(p, '.lj-jaren') == 1)
        p.close()
        p = pagina(ctx, 'wijk.html', 'wijk-overzicht')
        p.wait_for_selector('#gk a', timeout=20000)
        p.wait_for_timeout(500)
        uitslag('g5 overzicht heeft geen tijdlijn', n(p, '.lijnhost') == 0 and n(p, '.lijnbox') == 0)
        p.close()
        wslug = jl('wijken.json')['wijken'][0]['slug']
        p = pagina(ctx, f'wijk.html#w-{wslug}', 'wijk-wijk')
        p.wait_for_selector('#wijk h1', timeout=20000)
        p.wait_for_timeout(500)
        uitslag(f'g6 wijk (#w-{wslug}) heeft geen tijdlijn', n(p, '.lijnhost') == 0)
        p.close()

        # ---------- (j) mobiel 390 px ----------
        m = br.new_context(viewport={'width': 390, 'height': 800}, locale='nl-NL', is_mobile=True, has_touch=True)
        m.add_init_script(RUSTIG)
        p = pagina(m, 'dossier.html#parkeren', 'mobiel')
        laad_lijn(p)
        p.locator('#k-tijdlijn .kkop').click()
        p.wait_for_selector('.lj-jaren')
        p.wait_for_timeout(300)
        geom = p.evaluate("""()=>{const e=document.querySelector('.lj-jaren .lj-e.c')||document.querySelector('.lj-jaren .lj-e');const n=e.querySelector('.lj-kn').getBoundingClientRect(),k=e.querySelector('.lj-k').getBoundingClientRect();
          return {sw:document.documentElement.scrollWidth,iw:innerWidth,node:n.left,kaart:k.left,kw:k.width,kl:getComputedStyle(e.querySelector('.lj-kl')).position}}""")
        uitslag('j1 390 px: één kolom (knooppunt links van de kaart), kantlabel zichtbaar, geen horizontale scroll', geom['sw'] <= geom['iw'] and geom['node'] < geom['kaart'] and geom['kw'] > 250 and geom['kl'] == 'static', str(geom))
        p.locator('.lj-jaren').scroll_into_view_if_needed()
        p.locator('.lj-strook').scroll_into_view_if_needed()
        p.screenshot(path=SHOTS + 'mobiel.png')
        p.locator('[data-fa]').click()
        p.locator('.lj-e.c').first.scroll_into_view_if_needed()
        p.screenshot(path=SHOTS + 'mobiel-college.png')
        p.close()
        p = pagina(m, 'dossier.html#cameratoezicht', 'mobiel2')
        laad_lijn(p)
        p.locator('[data-tg]').click()
        p.wait_for_selector('.lj-jaren')
        sw = p.evaluate('[document.documentElement.scrollWidth,innerWidth]')
        uitslag('j2 390 px dossier zonder extra: geen horizontale scroll', sw[0] <= sw[1], str(sw))
        p.close()
        m.close()

        # ---------- (k) donker ----------
        d = br.new_context(viewport={'width': 1280, 'height': 900}, locale='nl-NL', color_scheme='dark')
        d.add_init_script(RUSTIG)
        p = pagina(d, 'dossier.html#parkeren', 'donker')
        laad_lijn(p)
        p.locator('#k-tijdlijn .kkop').click()
        p.wait_for_selector('.lj-jaren')
        p.locator('[data-fa]').click()
        p.locator('#k-tijdlijn').scroll_into_view_if_needed()
        p.wait_for_timeout(300)
        p.screenshot(path=SHOTS + 'donker.png')
        uitslag('k donker thema: screenshot gemaakt', True, SHOTS + 'donker.png')
        p.close()
        d.close()

        # ---------- (l) regressie andere pagina's ----------
        vid = jl('verg/index.json')[0]['id']
        for u in ['zoek.html#q=parkeren', f'vergadering.html?id={vid}']:
            p = pagina(ctx, u, u)
            p.wait_for_timeout(4000)
            p.close()

    print('\n=== console- en paginafouten ===')
    echt = []
    for naam, soort, tekst in FOUTEN:
        negeer = ('/api/' in tekst) or ('Failed to load resource' in tekst) or ('sdk.companywebcast' in tekst) or ('connectlive' in tekst)
        print(('  (genegeerd) ' if negeer else '  ') + f'[{naam}] {soort}: {tekst[:200]}')
        if not negeer:
            echt.append((naam, tekst))
    uitslag('l2 geen console- of paginafouten op alle geteste pagina\'s (zoek, vergadering, dossier, wijk)', not echt, str(echt[:3]))
    print('\n=== samenvatting ===')
    fout = [x for x, ok in RES if not ok]
    print(f'{len(RES) - len(fout)} van {len(RES)} controles geslaagd')
    for x in fout:
        print('  FOUT:', x)
    sys.exit(1 if fout else 0)


if __name__ == '__main__':
    main()
