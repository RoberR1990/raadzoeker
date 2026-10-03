# Kaart van Rotterdam voor de ontwerpschermen -> docs/ontwerp/kaart.json
# Bronnen (open data, in WERK/kaart/):
#   wijken.json  CBS wijken 2024 via PDOK WFS (wijkenbuurten:wijken, gemeentecode GM0599, EPSG:4326)
#   water.json   BRT TOP10NL waterdeel_vlak via PDOK OGC API (bbox 3.95,51.83,4.62,52.02), gefilterd op breed water
# Lagen: havens/bedrijfsgebieden grijs, de 14 gebieden (kleur in de pagina), water er blauw overheen, labels.
import json,math,os
from paden import WERK,DOCS
NAAM={'Rotterdam Centrum':'Centrum'}   # CBS-naam -> gebiedsnaam in de Raadzoeker
GEBIED={'Centrum','Delfshaven','Overschie','Noord','Hillegersberg-Schiebroek','Kralingen-Crooswijk','Feijenoord','IJsselmonde',
        'Pernis','Prins Alexander','Charlois','Hoogvliet','Hoek van Holland','Rozenburg'}
LON0,LON1,LAT0,LAT1=4.03,4.63,51.845,52.012   # uitsnede: Maasvlakte valt weg, Hoek van Holland net erin
kx=math.cos(math.radians((LAT0+LAT1)/2)); W=1000; S=W/((LON1-LON0)*kx); H=round((LAT1-LAT0)*S)
def xy(lon,lat): return ((lon-LON0)*kx*S,(LAT1-lat)*S)
def dp(pts,eps):
    if len(pts)<3: return pts
    a,b=pts[0],pts[-1]; dx,dy=b[0]-a[0],b[1]-a[1]; L=math.hypot(dx,dy)
    if L<1e-9: i=max(range(len(pts)),key=lambda k:math.hypot(pts[k][0]-a[0],pts[k][1]-a[1])); return dp(pts[:i+1],eps)[:-1]+dp(pts[i:],eps)
    i,dm=0,0
    for k in range(1,len(pts)-1):
        d=abs(dy*pts[k][0]-dx*pts[k][1]+b[0]*a[1]-b[1]*a[0])/L
        if d>dm: i,dm=k,d
    return dp(pts[:i+1],eps)[:-1]+dp(pts[i:],eps) if dm>eps else [a,b]
def opp(p): return abs(sum(p[i][0]*p[i-1][1]-p[i-1][0]*p[i][1] for i in range(len(p))))/2
def zw(p):
    A=sum(p[i][0]*p[i-1][1]-p[i-1][0]*p[i][1] for i in range(len(p)))/2 or 1e-9
    cx=sum((p[i][0]+p[i-1][0])*(p[i][0]*p[i-1][1]-p[i-1][0]*p[i][1]) for i in range(len(p)))/(6*A)
    cy=sum((p[i][1]+p[i-1][1])*(p[i][0]*p[i-1][1]-p[i-1][0]*p[i][1]) for i in range(len(p)))/(6*A)
    return cx,cy
def pad(coords,eps,minopp=0):
    d='';ringen=[]
    for poly in coords:
        for ring in poly:
            pts=dp([xy(x,y) for x,y in ring],eps)
            if len(pts)>=4 and opp(pts)>=minopp:
                d+='M'+' '.join(f'{x:.1f},{y:.1f}' for x,y in pts)+'Z'; ringen.append(pts)
    return d,ringen
def geom(g): return [g['coordinates']] if g['type']=='Polygon' else g['coordinates']
def main():
    wk=json.load(open(os.path.join(WERK,'kaart','wijken.json'),encoding='utf8'))
    wat=json.load(open(os.path.join(WERK,'kaart','water.json'),encoding='utf8'))
    gebieden=[];havens=[]
    for f in wk['features']:
        p=f['properties']; nm=NAAM.get(p['wijknaam'],p['wijknaam'])
        if p['water']=='JA': continue
        d,ringen=pad(geom(f['geometry']),0.6)
        if not d: continue
        if nm in GEBIED:
            groot=max(ringen,key=opp); cx,cy=zw(groot)
            gebieden.append({'naam':nm,'inw':max(0,p.get('aantalInwoners') or 0),'d':d,'lx':round(cx),'ly':round(cy)})
        else: havens.append(d)
    def binnen(pt,ring):
        x,y=pt;c=False
        for i in range(len(ring)):
            (x1,y1),(x2,y2)=ring[i-1],ring[i]
            if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1+1e-12)+x1: c=not c
        return c
    land=[]   # ringen van alle wijken (gebieden en havens), om water buiten de gemeente weg te laten
    for f in wk['features']:
        if f['properties']['water']=='JA': continue
        for poly in geom(f['geometry']):
            r=[xy(x,y) for x,y in poly[0]]; land.append((r,min(p[0] for p in r),max(p[0] for p in r),min(p[1] for p in r),max(p[1] for p in r)))
    water=''
    for f in wat['features']:
        d,ringen=pad(geom(f['geometry']),0.7,minopp=6)
        if not ringen: continue
        groot=max(ringen,key=opp); c=zw(groot); A=opp(groot)
        raakt=any(c[0]>=a and c[0]<=b and c[1]>=y0 and c[1]<=y1 and binnen(c,r) for r,a,b,y0,y1 in land)
        if raakt or A>3000: water+=d   # in de gemeente, of een grote rivier/zee
    out={'w':W,'h':H,'gebieden':gebieden,'havens':''.join(havens),'water':water,
         'bron':'CBS Wijk- en buurtkaart 2024 en BRT TOP10NL (Kadaster), via PDOK'}
    json.dump(out,open(os.path.join(DOCS,'ontwerp','kaart.json'),'w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
    print(W,H,len(gebieden),'gebieden',len(havens),'havens',round(os.path.getsize(os.path.join(DOCS,'ontwerp','kaart.json'))/1000),'kB')

if __name__=='__main__': main()