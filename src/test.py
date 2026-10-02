import asyncio,time,sys,json
from paden import DOCS; URL='file:///'+DOCS.replace(chr(92),'/')+'/'
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        ctx=await b.new_context(viewport={'width':1280,'height':900})
        await ctx.grant_permissions(['clipboard-read','clipboard-write'])
        pg=await ctx.new_page()
        errs=[]
        pg.on('console',lambda m: errs.append(m.text) if m.type in('error','warning') else None)
        pg.on('pageerror',lambda e: errs.append('PAGEERR '+str(e)))
        t=time.time()
        await pg.goto(URL+'raadzoeker.html')
        await pg.wait_for_function("document.getElementById('loadtxt').textContent.includes('spreekbeurten')",timeout=120000)
        print('loaded in',round(time.time()-t,1),'s |',await pg.inner_text('#loadtxt'))
        await pg.screenshot(path='s_browse.png')
        async def q(**kw):
            for k,v in kw.items():
                if k=='ww': await pg.set_checked('#ww',v)
                elif k in('fp','fr','fk'): await pg.select_option('#'+k,v)
                else: await pg.fill('#'+k,v)
            t=time.time()
            await pg.evaluate("lastKey='';update(false)")
            n=await pg.inner_text('.summary .n') if await pg.query_selector('.summary .n') else 'browse'
            print(kw,'->',n,'|',round((time.time()-t)*1000),'ms')
        await q(q='betaald parkeren')
        await pg.screenshot(path='s_res.png')
        await q(q='parkeren',q2='delfshaven')
        await q(q='parkeernorm',q2='',ww=True)
        await q(q='',fs='Velden',ww=False)
        await q(fs='',fp='DENK',fr='raad',fd1='2025-01-01')
        await q(fp='',fr='',fd1='2026-10-01',fd2='2026-10-01')
        await pg.screenshot(path='s_tl.png')
        await q(fd1='',fd2='',q='spreidingswet')
        # copy citation
        await pg.click('.card [data-act=copy]')
        print('CLIP:',await pg.evaluate('navigator.clipboard.readText()'))
        await pg.click('.card [data-act=read]')
        await pg.wait_for_timeout(300)
        await pg.screenshot(path='s_reader.png')
        print('reader title:',await pg.inner_text('#rtitle'),'| blocks',await pg.eval_on_selector_all('#rbody .sp','e=>e.length'))
        await pg.keyboard.press('Escape')
        mem=await pg.evaluate('performance.memory?performance.memory.usedJSHeapSize/1e6:0')
        print('heap MB',round(mem),'hash',await pg.evaluate('location.hash'))
        print('errors',errs[:5])
        # mobile
        await pg.set_viewport_size({'width':390,'height':800}); await pg.wait_for_timeout(200)
        await pg.screenshot(path='s_mobile.png')
        print('hscroll',await pg.evaluate('document.documentElement.scrollWidth>innerWidth'))
        await b.close()
asyncio.run(main())
