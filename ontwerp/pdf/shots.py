# Schermafdrukken van de site voor de pdf (lokale server op 8765)
from playwright.sync_api import sync_playwright
B = 'http://localhost:8765/ontwerp/'
SHOTS = [('verg', 'vergadering.html?id=9f0ee187', None), ('zoek', 'zoek.html?q=woonfraude', None),
         ('park', 'dossier.html#parkeren', None), ('wijk', 'wijk.html#delfshaven', None)]
with sync_playwright() as p:
    b = p.chromium.launch(channel='msedge', headless=True)
    pg = b.new_page(viewport={'width': 1280, 'height': 860}, device_scale_factor=2)
    pg.add_init_script("for (const k of ['rz-welkom']) localStorage.setItem(k,'nee'); for (const t of ['vergadering','zoek','dossier','wijk','vergaderingen']) localStorage.setItem('rz-tour-'+t,'ja');")
    for naam, url, _ in SHOTS:
        pg.goto(B + url); pg.wait_for_timeout(6000)
        pg.screenshot(path=f'ontwerp/pdf/{naam}.png')
    b.close()
