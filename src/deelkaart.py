# Deelkaarten (1200x630) voor alle dossiers in d/index.json (domeinen, onderwerpen, thema's, gebieden; geen kruisingen)
#   -> docs/deel/<slug>.png + <slug>.html + deel/index.json (lijst slugs; ontwerp.js linkt alleen naar een deelpagina die bestaat).
# De .html heeft og:-gegevens voor een voorvertoning in Teams/WhatsApp en stuurt door naar dossier.html#slug of wijk.html#slug.
# Cijfers volgen de telregel van docs/tel.js (bron d/<slug>.json, of het beloftespoor in d/<slug>-extra.json als dat bestaat).
# Lettertype: map in env RZ_FONTS (met arial.ttf en arialbd.ttf); anders Windows-map, anders Liberation Sans, anders DejaVu Sans.
# Let op: achter Cloudflare Access kan Teams de voorvertoning alleen ophalen als /deel/ buiten Access valt.
import json,os,re,unicodedata,html
from PIL import Image,ImageDraw,ImageFont
from paden import DOCS
SITE='https://raadzoeker.nl/'
ZOEK=[(os.environ.get('RZ_FONTS') or '',('arial.ttf','arialbd.ttf')),(r'C:\Windows\Fonts',('arial.ttf','arialbd.ttf')),
      ('/usr/share/fonts/truetype/liberation',('LiberationSans-Regular.ttf','LiberationSans-Bold.ttf')),('/usr/share/fonts/liberation',('LiberationSans-Regular.ttf','LiberationSans-Bold.ttf')),
      ('/usr/share/fonts/truetype/liberation2',('LiberationSans-Regular.ttf','LiberationSans-Bold.ttf')),('/usr/share/fonts/truetype/dejavu',('DejaVuSans.ttf','DejaVuSans-Bold.ttf'))]
FONT={}
for m,(r_,b_) in ZOEK:
    if m and os.path.exists(os.path.join(m,r_)) and os.path.exists(os.path.join(m,b_)): FONT={'arial.ttf':os.path.join(m,r_),'arialbd.ttf':os.path.join(m,b_)}; break
def font(n,s):
    if not FONT: raise SystemExit('geen lettertype gevonden: zet RZ_FONTS op een map met arial.ttf en arialbd.ttf (of installeer fonts-liberation)')
    return ImageFont.truetype(FONT[n],s)
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
LABEL={'domein':'Dossier','onderwerp':'Onderwerp','thema':'Thema','gebied':'Gebied'}
def tel(d,X,stand):
    """telregel, gelijk aan telling() in docs/tel.js"""
    if X and X.get('spoor'):
        def laat(x):
            l=(x.get('stappen') or [None])[-1]; return bool(l) and l[1]=='verwacht' and l[0]<stand
        op=[x for x in X['spoor'] if x['open']]; mo=[x for x in op if x['soort']=='motie']; tz=[x for x in op if x['soort']=='toezegging']
        aan=(X.get('tel') or {}).get('aan',sum(1 for x in X['spoor'] if x['soort']=='motie'))
        return dict(sinds='2022',aan=aan,af=max(0,aan-len(mo)),mo=len(mo),mo_laat=sum(map(laat,mo)),tz=len(tz),tz_laat=sum(map(laat,tz)))
    m,z=d['moties'],d['toez']
    return dict(sinds='2018',aan=m['aangenomen'],af=m['afgedaan'],mo=m['open'],mo_laat=m['te_laat'],tz=z['open'],tz_laat=z['te_laat'])
def kaart(dd,T,stand):
    W,H=1200,630; im=Image.new('RGB',(W,H),GRIJS); d=ImageDraw.Draw(im)
    d.rectangle([0,0,W,96],fill=GROEN); logo(d,48,20,(255,255,255))
    d.text((112,30),'raadzoeker',font=font('arialbd.ttf',34),fill=(255,255,255))
    d.text((300,38),'onofficieel · wat de Rotterdamse raad zei en besloot',font=font('arial.ttf',22),fill=(255,255,255))
    d.rounded_rectangle([48,128,W-48,H-48],radius=16,fill=(255,255,255))
    d.text((88,160),LABEL[dd['soort']],font=font('arial.ttf',26),fill=SUB)
    fs=72
    while fs>38 and font('arialbd.ttf',fs).getlength(dd['naam'])>W-176: fs-=2
    d.text((88,196),dd['naam'],font=font('arialbd.ttf',fs),fill=ZWART)
    def laat(n): return f'waarvan {n} over de termijn' if n else 'geen over de termijn'
    kpi=[(nf(T['aan']),'moties aangenomen',f"sinds {T['sinds']} · {nf(T['af'])} afgedaan"),(nf(T['mo']),'moties in uitvoering',laat(T['mo_laat'])),(nf(T['tz']),'toezeggingen open',laat(T['tz_laat']))]
    for i,(n,a,b) in enumerate(kpi):
        x=88+i*258
        d.text((x,318),n,font=font('arial.ttf',64),fill=ZWART)
        d.text((x,398),a,font=font('arial.ttf',24),fill=ZWART)
        if b.startswith('waarvan'):
            d.ellipse([x,438,x+14,452],fill=LAAT); d.text((x+22,430),b,font=font('arial.ttf',19),fill=ZWART)
        else: d.text((x,430),b,font=font('arial.ttf',19),fill=SUB)
    # trend: aandacht per jaar
    v=dd['trend']; mx=max(v) or 1; x0,y0,bw,hh=892,450,22,130
    d.text((x0,280),'Aandacht per jaar',font=font('arial.ttf',21),fill=SUB)
    for i,val in enumerate(v):
        h=max(3,val/mx*hh); x=x0+i*(bw+4)
        d.rectangle([x,y0-h,x+bw,y0],fill=(153,204,160) if i==len(v)-1 else GROEN)
    d.text((x0,y0+8),'2018',font=font('arial.ttf',18),fill=SUB); d.text((x0+9*(bw+4)-60,y0+8),'2026',font=font('arial.ttf',18),fill=SUB)
    d.text((88,H-100),f"Stand {stand} · tellingen sinds {T['sinds']} · raadzoeker.nl",font=font('arial.ttf',21),fill=SUB)
    return im
def laad(p):
    try: return json.load(open(p,encoding='utf8'))
    except OSError: return None
def main():
    od=DOCS; ix=laad(os.path.join(od,'d','index.json')); out=os.path.join(od,'deel'); os.makedirs(out,exist_ok=True)
    stand_iso=ix['stand']; stand='-'.join(reversed(stand_iso.split('-'))); gedaan=[]
    sigp=os.path.join(out,'sig.json'); SIG=laad(sigp) or {}   # alleen opnieuw tekenen als de inhoud verandert (anders elke nacht 75 nieuwe png's in git)
    for x in ix['d']:
        if x['soort'] not in LABEL: continue
        s=x['slug']; dd=laad(os.path.join(od,'d',s+'.json'))
        if not dd: continue
        T=tel(dd,laad(os.path.join(od,'d',s+'-extra.json')),stand_iso)
        sig=json.dumps([dd['naam'],dd['soort'],T,dd['trend']],sort_keys=True)
        if SIG.get(s)==sig and os.path.exists(os.path.join(out,s+'.png')) and os.path.exists(os.path.join(out,s+'.html')): gedaan.append(s); continue
        SIG[s]=sig; kaart(dd,T,stand).save(os.path.join(out,s+'.png'),optimize=True)
        doel=('../wijk.html#' if dd['soort']=='gebied' else '../dossier.html#')+s
        titel=html.escape(f"{dd['naam']} in de Rotterdamse raad",quote=True)
        laat=T['mo_laat']+T['tz_laat']
        oms=html.escape(f"{nf(T['aan'])} moties aangenomen (sinds {T['sinds']}), {nf(T['mo'])} in uitvoering, {nf(T['tz'])} toezeggingen open{f', waarvan {laat} over de termijn' if laat else ''}. Onofficieel overzicht uit openbare raadsinformatie.",quote=True)
        open(os.path.join(out,s+'.html'),'w',encoding='utf8').write(f'''<!doctype html><html lang="nl"><head><meta charset="utf-8"><meta name="robots" content="noindex">
<title>{titel} · raadzoeker</title><meta property="og:title" content="{titel}"><meta property="og:description" content="{oms}">
<meta property="og:image" content="{SITE}deel/{s}.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:url" content="{SITE}deel/{s}.html"><meta name="twitter:card" content="summary_large_image">
<script>(function(){{var d="{doel}",s=location.search;if(s){{var i=d.indexOf("#");d=i<0?d+s:d.slice(0,i)+s+d.slice(i);}}location.replace(d);}})();</script><meta http-equiv="refresh" content="0;url={doel}"></head><body><p><a href="{doel}">{titel}</a></p></body></html>''')
        gedaan.append(s)
    json.dump(SIG,open(sigp,'w',encoding='utf8'),sort_keys=True,separators=(',',':'))
    json.dump(sorted(gedaan),open(os.path.join(out,'index.json'),'w',encoding='utf8'),separators=(',',':'))
    print(len(gedaan),'deelkaarten',sum(os.path.getsize(os.path.join(out,f)) for f in os.listdir(out))//1000,'kB')
if __name__=='__main__': main()
