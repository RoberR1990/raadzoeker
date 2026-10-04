# Fase 2c: straatnamen (BAG) per CBS-buurt, voor het herkennen van straten in raadsstukken.
#   python src/bag_straten.py   -> WERK/gebied/straten.json {straat: {woonplaats, buurten: {buurtcode: aantal adressen}}}
# Bron: PDOK BAG WFS, verblijfsobjecten van gemeente Rotterdam (identificatie 0599*), in tegels van 0,02 graad opgehaald
# (de WFS staat geen startIndex boven 50.000 toe). Elk adres wordt met punt-in-polygoon aan een CBS-buurt (2024) gekoppeld.
# Hervatbaar: per buurt een cachebestand in WERK/gebied/bag/.
import json,os,time,urllib.request,urllib.parse,collections
from paden import WERK

URL='https://service.pdok.nl/lv/bag/wfs/v2_0'
def FILTER(b):   # bbox in het filter: de WFS staat BBOX en FILTER niet samen toe
    return ('<Filter xmlns="http://www.opengis.net/fes/2.0" xmlns:gml="http://www.opengis.net/gml/3.2"><And>'
            '<PropertyIsLike wildCard="*" singleChar="." escapeChar="!"><ValueReference>identificatie</ValueReference><Literal>0599*</Literal></PropertyIsLike>'
            f'<BBOX><ValueReference>geom</ValueReference><gml:Envelope srsName="urn:ogc:def:crs:EPSG::4326"><gml:lowerCorner>{b[1]} {b[0]}</gml:lowerCorner>'
            f'<gml:upperCorner>{b[3]} {b[2]}</gml:upperCorner></gml:Envelope></BBOX></And></Filter>')
D=os.path.join(WERK,'gebied'); C=os.path.join(D,'bag')

def ringen(geom):
    if geom['type']=='Polygon': return [geom['coordinates'][0]]
    return [p[0] for p in geom['coordinates']]

def binnen(x,y,r):
    c=False
    for i in range(len(r)):
        (x1,y1),(x2,y2)=r[i-1],r[i]
        if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1+1e-12)+x1: c=not c
    return c

def haal(bbox):
    out=[]; start=0
    while True:
        q=dict(service='WFS',version='2.0.0',request='GetFeature',typeNames='bag:verblijfsobject',count='1000',startIndex=str(start),
               outputFormat='application/json',srsName='EPSG:4326',propertyName='identificatie,openbare_ruimte,woonplaats,geom',filter=FILTER(bbox))
        for poging in range(4):
            try:
                with urllib.request.urlopen(URL+'?'+urllib.parse.urlencode(q),timeout=120) as r: j=json.load(r); break
            except Exception as e:
                print('  opnieuw',e); time.sleep(5*(poging+1))
        else: raise SystemExit('PDOK reageert niet')
        fs=j.get('features',[]); time.sleep(1)
        out+=[(f['properties']['identificatie'],f['properties']['openbare_ruimte'],f['properties']['woonplaats'],f['geometry']['coordinates']) for f in fs if f.get('geometry')]
        if len(fs)<1000: return out
        start+=1000
        if start>=50000: raise SystemExit('meer dan 50.000 in één bbox')

def main():
    os.makedirs(C,exist_ok=True)
    B=json.load(open(os.path.join(WERK,'kaart','buurten_2024.json'),encoding='utf8'))['features']
    R=[]   # (buurtcode, ring, bbox)
    for f in B:
        if f['properties'].get('water')=='JA': continue
        for r in ringen(f['geometry']): R.append((f['properties']['buurtcode'],r,min(x for x,_ in r),max(x for x,_ in r),min(y for _,y in r),max(y for _,y in r)))
    x0=min(r[2] for r in R); x1=max(r[3] for r in R); y0=min(r[4] for r in R); y1=max(r[5] for r in R); S=0.02
    tegels=[(x0+i*S,y0+j*S,x0+(i+1)*S,y0+(j+1)*S) for i in range(int((x1-x0)/S)+1) for j in range(int((y1-y0)/S)+1)]
    for t in tegels:
        p=os.path.join(C,'t_%.2f_%.2f.json'%(t[0],t[1]))
        if os.path.exists(p): continue
        alle=haal(t); uit=[]
        for a in alle:
            x,y=a[3][0],a[3][1]; code=next((c for c,r,a1,b1,c1,d1 in R if a1<=x<=b1 and c1<=y<=d1 and binnen(x,y,r)),None)
            uit.append(list(a[:3])+[code])
        json.dump(uit,open(p,'w',encoding='utf8'),ensure_ascii=False)
        if alle: print('%.2f %.2f'%(t[0],t[1]),len(alle),'adressen,',sum(1 for u in uit if u[3] is None),'zonder buurt',flush=True)
    st=collections.defaultdict(lambda:{'wp':collections.Counter(),'b':collections.Counter()}); gezien=set()
    import glob
    for p in glob.glob(os.path.join(C,'t_*.json')):
        for i,s,wp,code in json.load(open(p,encoding='utf8')):
            if i in gezien or code is None: continue
            gezien.add(i); st[s]['b'][code]+=1; st[s]['wp'][wp]+=1
    out={s:{'woonplaats':v['wp'].most_common(1)[0][0],'buurten':dict(v['b'].most_common())} for s,v in st.items()}
    json.dump(out,open(os.path.join(D,'straten.json'),'w',encoding='utf8'),ensure_ascii=False)
    print(len(out),'straten,',len(gezien),'adressen')

if __name__=='__main__': main()
