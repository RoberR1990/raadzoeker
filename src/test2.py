import asyncio,time
from paden import DOCS; URL='file:///'+DOCS.replace(chr(92),'/')+'/'
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        ctx=await b.new_context(viewport={'width':1280,'height':900},locale='nl-NL')
        await ctx.grant_permissions(['clipboard-read','clipboard-write'])
        pg=await ctx.new_page(); errs=[]
        pg.on('console',lambda m: errs.append(m.text) if m.type in('error',) else None)
        pg.on('pageerror',lambda e: errs.append('PAGEERR '+str(e)))
        await pg.goto(URL+'raadzoeker.html#q=parkeernorm&fp=VVD')
        await pg.wait_for_function("document.getElementById('loadtxt').textContent.includes('vergaderingen met')",timeout=120000)
        print('hash restore ->',await pg.inner_text('.summary .n'), '| fp=',await pg.input_value('#fp'))
        await pg.click('.card [data-act=full]'); print('full len',len(await pg.inner_text('.card .snip')))
        await pg.click('.years button[data-year="2023"]'); await pg.wait_for_timeout(100)
        print('year click ->',await pg.inner_text('.summary .n'),await pg.input_value('#fd1'),await pg.evaluate('location.hash'))
        await pg.click('#reset'); await pg.wait_for_timeout(100)
        # browse: open first meeting w/o notulen and one with
        ms=await pg.query_selector_all('details.yr[open] details.mt > summary')
        await ms[0].click(); await ms[1].click(); await pg.wait_for_timeout(100)
        its=await pg.query_selector_all('details.mt[open] li a')
        print('items in 2 meetings',len(its))
        await pg.screenshot(path='s_browse2.png')
        await its[5].click(); await pg.wait_for_timeout(200)
        print('reader(timeline):',await pg.inner_text('#rmeta'),'|',await pg.inner_text('#rtitle'),'| blocks',await pg.eval_on_selector_all('#rbody .sp','e=>e.length'))
        await pg.screenshot(path='s_reader_tl.png')
        await pg.click('#rnext'); await pg.wait_for_timeout(100); print(' next:',await pg.inner_text('#rtitle'))
        await pg.click('#rclose')
        # item in meeting with notulen
        lis=await pg.query_selector_all('details.mt[open]:nth-of-type(2) li a')
        await lis[min(12,len(lis)-1)].click(); await pg.wait_for_timeout(200)
        print('reader(notulen):',await pg.inner_text('#rtitle'),'| blocks',await pg.eval_on_selector_all('#rbody .sp','e=>e.length'))
        await pg.click('#rbody [data-act=rcopy]'); print('CLIP:',(await pg.evaluate('navigator.clipboard.readText()'))[-330:])
        await pg.keyboard.press('Escape')
        # speaker + agenda filter, kinds
        await pg.fill('#fs','Kasmi'); await pg.fill('#fa','onderwijs'); await pg.evaluate("lastKey='';update(false)")
        print('Kasmi+onderwijs ->',await pg.inner_text('.summary .n'))
        await pg.fill('#fs',''); await pg.fill('#fa',''); await pg.fill('#q','verzoekt het college'); await pg.select_option('#fk','1'); await pg.evaluate("lastKey='';update(false)")
        print('moties ->',await pg.inner_text('.summary .n'))
        await pg.screenshot(path='s_moties.png')
        print('errors',errs)
        await b.close()
asyncio.run(main())
