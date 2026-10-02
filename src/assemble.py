# template.html + meta -> één html-pagina. De jaardata zelf blijft als los bestand naast de pagina staan
# (OUT/JAAR.zst) en wordt in de browser opgehaald; meta krijgt de map (relatief t.o.v. de pagina) en een hash per jaar.
import json,sys,os,hashlib
from paden import SRC,DATA
tpl=open(f'{SRC}/template.html',encoding='utf8').read()
OUT=os.environ.get('RZ_OUT','out')
meta=json.load(open(os.environ.get('RZ_META',f'{OUT}/meta.json'),encoding='utf8'))
only=sys.argv[2].split(',') if len(sys.argv)>2 else None
if only: meta['years']=[y for y in meta['years'] if y['y'] in only]
for y in meta['years']:
    z=open(f"{OUT}/{y['y']}.zst",'rb').read(); assert len(z)==y['z'],y['y']
    y['h']=hashlib.sha1(z).hexdigest()[:10]
meta['dir']=os.path.relpath(OUT,os.path.dirname(os.path.abspath(sys.argv[1]))).replace(os.sep,'/')+'/'
fz=open(f'{SRC}/js/node_modules/fzstd/umd/index.js',encoding='utf8').read()
assert '</script' not in fz
if meta.get('kind')!='c':   # raad: themasamenvattingen (AI) uit data/tsum
    import glob
    meta['tsum']={d['id']:d for f in sorted(glob.glob(f'{DATA}/tsum/out_*.json')) for d in json.load(open(f,encoding='utf8'))}
    ib=os.path.join(os.path.dirname(os.path.abspath(sys.argv[1])),'data','ibabs')
    if os.path.exists(f'{ib}/stukken.zst'):   # officiële stukken uit iBabs (ibabs_emit.py)
        z=open(f'{ib}/stukken.zst','rb').read(); m=json.load(open(f'{ib}/meta.json',encoding='utf8'))
        meta['ibabs']={'h':hashlib.sha1(z).hexdigest()[:10],'n':m['n'],'per':m['per'],'stand':m.get('stand','')}
if meta.get('kind')=='c':   # commissies -> Commissiezoeker-teksten
    import variant; tpl=variant.apply(tpl,meta)
html=tpl.replace('/*META*/',json.dumps(meta,ensure_ascii=False).replace('</','<\\/')).replace('/*FZSTD*/','/* fzstd 0.1.1, MIT, (c) Arjun Barrett */\n'+fz)
open(sys.argv[1],'w',encoding='utf8').write(html)
print(sys.argv[1],len(html.encode())/1e6,'MB')
