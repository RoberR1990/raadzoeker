import asyncio,sys
from paden import DOCS; URL='file:///'+DOCS.replace(chr(92),'/')+'/'
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        pg=await b.new_page(viewport={'width':1280,'height':1100},locale='nl-NL'); errs=[]
        pg.on('console',lambda m: errs.append(m.text) if m.type=='error' and 'ERR_TUNNEL' not in m.text else None)
        pg.on('pageerror',lambda e: errs.append('PAGEERR '+str(e)))
        await pg.goto(URL+''+sys.argv[1])
        await pg.wait_for_function("document.getElementById('loadtxt').textContent.includes('spreekbeurten ·')",timeout=180000)
        print(await pg.inner_text('#loadtxt'),'|',await pg.inner_text('.sub'))
        await pg.screenshot(path='c_home.png')
        await pg.fill('#q','parkeer | parkeren'); await pg.evaluate('update(false)'); await pg.wait_for_timeout(500)
        print('parkeren:',await pg.inner_text('.summary .n'),'| cats',await pg.eval_on_selector_all('#fc option','e=>e.length'))
        await pg.screenshot(path='c_res.png')
        print(' card:',(await pg.inner_text('.card'))[:300].replace('\n',' / '))
        await pg.click('.card [data-act=read]'); await pg.wait_for_timeout(300); print(' reader:',(await pg.inner_text('#rmeta'))[:120],'|',await pg.eval_on_selector_all('#rbody .sp','e=>e.length')); await pg.keyboard.press('Escape')
        await pg.click('.tabs [data-view=z]'); await pg.wait_for_timeout(300); print('toez:',await pg.inner_text('.summary .n'))
        await pg.click('.tabs [data-view=i]'); await pg.wait_for_timeout(400); await pg.screenshot(path='c_ins.png'); print('ins headers:',await pg.eval_on_selector_all('.chart h3','e=>e.map(x=>x.textContent.slice(0,50))'))
        print('heap',round(await pg.evaluate('performance.memory.usedJSHeapSize/1e6')),'errors',errs)
        await b.close()
asyncio.run(main())
