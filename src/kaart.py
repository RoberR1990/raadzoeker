# Wijkgrenzen Rotterdam (CBS wijken 2024 via PDOK, open data) -> vereenvoudigde SVG-paden in docs/ontwerp/kaart.json
# Bron downloaden: zie CLAUDE.md (WFS wijkenbuurten:wijken, gemeentecode GM0599, EPSG:4326) naar WERK/kaart/wijken.json
import json,math,os
from paden import WERK,DOCS
NAAM={'Rotterdam Centrum':'Centrum'}   # CBS-naam -> themanaam in de Raadzoeker
WEG={'Botlek-Europoort-Maasvlakte','Rotterdam-Noord-West','Groot water'}   # te groot of zonder bewoners; laat de stad klein lijken
def dp(pts,eps):
    if len(pts)<3: return pts
    a,b=pts[0],pts[-1]; dx,dy=b[0]-a[0],b[1]-a[1]; L=math.hypot(dx,dy) or 1e-12
    i,dm=0,0
    for k in range(1,len(pts)-1):
        d=abs(dy*pts[k][0]-dx*pts[k][1]+b[0]*a[1]-b[1]*a[0])/L
        if d>dm: i,dm=k,d
    return dp(pts[:i+1],eps)[:-1]+dp(pts[i:],eps) if dm>eps else [a,b]
g=json.load(open(os.path.join(WERK,'kaart','wijken.json'),encoding='utf8'))
fs=[f for f in g['features'] if f['properties']['wijknaam'] not in WEG]
lat0=51.92; kx=math.cos(math.radians(lat0))
allp=[(x*kx,-y) for f in fs for poly in f['geometry']['coordinates'] for ring in poly for x,y in ring]
mnx=min(p[0] for p in allp); mxx=max(p[0] for p in allp); mny=min(p[1] for p in allp); mxy=max(p[1] for p in allp)
W=1000; s=W/(mxx-mnx); H=round((mxy-mny)*s)
out=[]
for f in fs:
    p=f['properties']; d=''
    for poly in f['geometry']['coordinates']:
        for ring in poly:
            pts=[((x*kx-mnx)*s,(-y-mny)*s) for x,y in ring]; h=len(pts)//2; pts=dp(pts[:h+1],0.8)[:-1]+dp(pts[h:],0.8)   # gesloten ring: in twee helften
            if len(pts)>=4: d+='M'+' '.join(f'{x:.0f},{y:.0f}' for x,y in pts)+'Z'
    nm=p['wijknaam']; out.append({'naam':NAAM.get(nm,nm),'water':p['water']=='JA','inw':max(0,p.get('aantalInwoners') or 0),'d':d})
json.dump({'w':W,'h':H,'wijken':out,'bron':'CBS Wijk- en buurtkaart 2024 (PDOK)'},open(os.path.join(DOCS,'ontwerp','kaart.json'),'w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
print(W,H,len(out),os.path.getsize(os.path.join(DOCS,'ontwerp','kaart.json'))//1000,'kB')
