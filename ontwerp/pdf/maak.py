# raadzoeker.html -> raadzoeker.pdf (A4, 3 bladzijden) en png per bladzijde ter controle
import pathlib
from playwright.sync_api import sync_playwright
d = pathlib.Path(__file__).parent.resolve()
with sync_playwright() as p:
    b = p.chromium.launch(channel='msedge', headless=True)
    pg = b.new_page()
    pg.goto((d / 'raadzoeker.html').as_uri()); pg.wait_for_timeout(1000)
    pg.pdf(path=str(d / 'raadzoeker.pdf'), format='A4', print_background=True, margin={'top': '0', 'bottom': '0', 'left': '0', 'right': '0'})
    pg.set_viewport_size({'width': 794, 'height': 1123}); pg.emulate_media(media='print')
    for i, el in enumerate(pg.query_selector_all('.blad')):
        el.screenshot(path=str(d / f'blad{i + 1}.png'))
    b.close()
