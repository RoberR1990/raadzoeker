# Zet de grote bronbestanden uit paden.BRON klaar in de werkmap:
#   raw/header.json, raw/agenda/JAAR/ID.html, raw/doc/ID.pdf  (uit de bundle)
#   subs.json   (ondertitels raad, beide delen samengevoegd)
#   cmeta.json  (commissies: agenda's en details)
# Bestaande uitvoer wordt overgeslagen.
import json,struct,gzip,os
from paden import BRON,BUNDLE,WERK,RAW
def bundle():
    if os.path.exists(os.path.join(RAW,'header.json')): print('raw: al aanwezig'); return
    with open(BUNDLE,'rb') as f:
        assert f.read(8)==b'RZBUNDL1','geen RZBUNDL1-bestand: '+BUNDLE
        n=struct.unpack('<I',f.read(4))[0]; h=json.loads(f.read(n))
        for x in h['files']:
            p=os.path.join(RAW,*x['name'].split('/')); os.makedirs(os.path.dirname(p),exist_ok=True)
            b=f.read(x['size']); assert len(b)==x['size'],x['name']
            open(p,'wb').write(b)
    json.dump({k:h[k] for k in h if k!='files'},open(os.path.join(RAW,'header.json'),'w'),ensure_ascii=False)
    print('raw:',len(h['meetings']),'vergaderingen',len(h['docs']),'documenten',len(h['files']),'bestanden')
def gz(names,out):
    p=os.path.join(WERK,out)
    if os.path.exists(p): print(out+': al aanwezig'); return
    d={}
    for n in names: d.update(json.load(gzip.open(os.path.join(BRON,n),'rt',encoding='utf8')))
    json.dump(d,open(p,'w'),ensure_ascii=False); print(out+':',len(d))
if __name__=='__main__':
    os.makedirs(WERK,exist_ok=True)
    bundle()
    gz(['raadzoeker-ondertitels.json.gz','raadzoeker-ondertitels-2.json.gz'],'subs.json')
    gz(['raadzoeker-commissies-meta.json.gz'],'cmeta.json')
