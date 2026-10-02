import json,sys
tpl=open('template.html',encoding='utf8').read()
import os
OUT=os.environ.get('RZ_OUT','out')
meta=json.load(open(os.environ.get('RZ_META',f'{OUT}/meta.json')))
only=sys.argv[2].split(',') if len(sys.argv)>2 else None
if only: meta['years']=[y for y in meta['years'] if y['y'] in only]
import numpy as np
ALPH=''.join(chr(c) for c in range(33,127) if c not in (60,62,38)); assert len(ALPH)==91
LUT=np.frombuffer(ALPH.encode(),dtype=np.uint8)
def enc91(b):
    bits=np.unpackbits(np.frombuffer(b,dtype=np.uint8))
    pad=(-len(bits))%13
    if pad: bits=np.concatenate([bits,np.zeros(pad,dtype=np.uint8)])
    v=bits.reshape(-1,13).astype(np.uint32)@(1<<np.arange(12,-1,-1,dtype=np.uint32))
    out=np.empty(len(v)*2,dtype=np.uint8); out[0::2]=LUT[v//91]; out[1::2]=LUT[v%91]
    return out.tobytes().decode('ascii')
data=''
for y in meta['years']:
    z=open(f"{OUT}/{y['y']}.zst",'rb').read(); assert len(z)==y['z']
    e=enc91(z); assert '</' not in e and '<!--' not in e
    data+='<script type="application/octet-stream" id="d%s">%s</script>\n'%(y['y'],e)
fz=open('js/node_modules/fzstd/umd/index.js').read()
assert '</script' not in fz
if OUT!='out':
    import variant; tpl=variant.apply(tpl,meta)
html=tpl.replace('/*META*/',json.dumps(meta,ensure_ascii=False).replace('</','<\\/')).replace('/*DATA*/',data).replace('/*FZSTD*/','/* fzstd 0.1.1, MIT, (c) Arjun Barrett */\n'+fz)
open(sys.argv[1],'w',encoding='utf8').write(html)
print(sys.argv[1],len(html.encode())/1e6,'MB')
