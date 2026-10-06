# Deelkaarten (1200x630) per onderwerp en gebied -> docs/ontwerp/deel/<slug>.png + <slug>.html
# De .html heeft og:-gegevens voor een voorvertoning in Teams/WhatsApp en stuurt door naar het onderwerp of de wijk.
# Let op: achter Cloudflare Access kan Teams de voorvertoning alleen ophalen als /ontwerp/deel/ buiten Access valt.
import json,os,re,unicodedata
from PIL import Image,ImageDraw,ImageFont
from paden import DOCS
SITE='https://publieke-tribune.pages.dev/ontwerp/'
F=r'C:\Windows\Fonts'
def font(n,s): return ImageFont.truetype(os.path.join(F,n),s)
GROEN=(0,129,31); DGROEN=(0,76,49); ZACHT=(225,239,226); ZWART=(0,0,0); SUB=(62,75,80); GRIJS=(239,244,246); LAAT=(229,110,2)
def slug(s):
    s=unicodedata.normalize('NFD',s.lower()); s=''.join(c for c in s if unicodedata.category(c)!='Mn').replace('&',' ')
    return re.sub(r'[^a-z0-9]+','-',s).strip('-')
def nf(n): return f'{n:,}'.replace(',','.')
def logo(d,x,y,kleur):
    import math
    for i in range(9):
        a=math.pi*(1-i/8); cx=x+26+20*math.cos(a); cy=y+28-20*math.sin(a)
        d.ellipse([cx-4,cy-4,cx+4,cy+4],fill=kleur)
    d.ellipse([x+21,y+21,x+31,y+31],fill=kleur)
def kaart(dd,stand):
    W,H=1200,630; im=Image.new('RGB',(W,H),GRIJS); d=ImageDraw.Draw(im)
    d.rectangle([0,0,W,96],fill=GROEN)
    ic=Image.open(os.path.join(DOCS,'ontwerp','img','tribune-icoon-wit.png')); ic.thumbnail((80,64)); im.paste(ic,(40,(96-ic.size[1])//2),ic)
    d.text((130,28),'De Publieke Tribune',font=font('arialbd.ttf',34),fill=(255,255,255))
    d.text((470,40),'onofficieel · wat de Rotterdamse raad zegt, besluit en belooft',font=font('arial.ttf',22),fill=(255,255,255))
    d.rounded_rectangle([48,128,W-48,H-48],radius=16,fill=(255,255,255))
    d.text((88,160),dd['groep'],font=font('arial.ttf',26),fill=SUB)
    t=dd['naam']; fs=72 if len(t)<20 else 56 if len(t)<30 else 44
    d.text((88,196),t,font=font('arialbd.ttf',fs),fill=ZWART)
    m,tz=dd['moties'],dd['toez']
    kpi=[(nf(m['aangenomen']),'aangenomen moties','sinds 2018'),(nf(m['open']),'moties in uitvoering',f"{m['te_laat']} over de termijn"),(nf(tz['open']),'toezeggingen open',f"{tz['te_laat']} over de termijn")]
    for i,(n,a,b) in enumerate(kpi):
        x=88+i*250
        d.text((x,318),n,font=font('arial.ttf',64),fill=ZWART)
        d.text((x,398),a,font=font('arial.ttf',24),fill=ZWART)
        if 'termijn' in b and not b.startswith('0'):
            d.ellipse([x,438,x+14,452],fill=LAAT); d.text((x+22,430),b,font=font('arial.ttf',21),fill=ZWART)
        else: d.text((x,430),b,font=font('arial.ttf',21),fill=SUB)
    # trend: aandacht per jaar
    v=dd['trend']; mx=max(v) or 1; x0,y0,bw,hh=830,450,26,130
    d.text((x0,280),'Aandacht per jaar',font=font('arial.ttf',21),fill=SUB)
    for i,val in enumerate(v):
        h=max(3,val/mx*hh); x=x0+i*(bw+6)
        d.rectangle([x,y0-h,x+bw,y0],fill=(153,204,160) if i==len(v)-1 else GROEN)
    d.text((x0,y0+8),'2018',font=font('arial.ttf',18),fill=SUB); d.text((x0+8*(bw+6)-18,y0+8),'2026',font=font('arial.ttf',18),fill=SUB)
    d.text((88,H-100),f'Stand {stand} · publieke-tribune.pages.dev',font=font('arial.ttf',21),fill=SUB)
    return im
def main():
    D=json.load(open(os.path.join(DOCS,'ontwerp','dossiers.json'),encoding='utf8')); out=os.path.join(DOCS,'ontwerp','deel'); os.makedirs(out,exist_ok=True)
    stand='-'.join(reversed(D['stand'].split('-')))
    for dd in D['dossiers']:
        s=slug(dd['naam']); wijk=dd['groep']=='Wijken en gebieden' and 'inw' in dd
        kaart(dd,stand).save(os.path.join(out,s+'.png'),optimize=True)
        doel=('../wijk.html#' if wijk else '../dossier.html#')+s
        titel=f"{dd['naam']} in de Rotterdamse raad"
        oms=f"{nf(dd['moties']['aangenomen'])} aangenomen moties sinds 2018, {dd['moties']['open']} in uitvoering, {dd['toez']['open']} toezeggingen open. Onofficieel overzicht uit openbare raadsinformatie."
        open(os.path.join(out,s+'.html'),'w',encoding='utf8').write(f'''<!doctype html><html lang="nl"><head><meta charset="utf-8"><meta name="robots" content="noindex">
<title>{titel} · De Publieke Tribune</title><meta property="og:title" content="{titel}"><meta property="og:description" content="{oms}">
<meta property="og:image" content="{SITE}deel/{s}.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:url" content="{SITE}deel/{s}.html"><meta name="twitter:card" content="summary_large_image">
<meta http-equiv="refresh" content="0;url={doel}"></head><body><p><a href="{doel}">{titel}</a></p></body></html>''')
    print(len(D['dossiers']),'deelkaarten',sum(os.path.getsize(os.path.join(out,f)) for f in os.listdir(out))//1000,'kB')
if __name__=='__main__': main()
