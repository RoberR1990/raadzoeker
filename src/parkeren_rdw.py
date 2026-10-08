# Betaald parkeren door de jaren, uit RDW Open Data Parkeren (gebiedsbeheerder 599 = Rotterdam).
#   python src/parkeren_rdw.py  -> WERK/parkeren/*.json (ruw) en docs/d/parkeren-kaart.json
# Per parkeerzone (contour uit GEOMETRIE GEBIED) en per jaar (peildatum 1 juli; 2026: de stand van vandaag):
# geldt er betaald parkeren (GEBIED REGELING, gebruik BETAALDP), en wat kost een uur op een woensdag om 12:00
# (REGELING -> TIJDVAK -> TARIEFDEEL). Ook de regelingen die al in de toekomst ingaan (zoals uitbreidingen in 2026) worden meegenomen.
import json,os,re,urllib.request,urllib.parse,datetime,collections
from paden import WERK,DOCS,STAND
import kaart as K
RDW='https://opendata.rdw.nl/resource/'
SETS={'gebied':'adw6-9hsg','geometrie':'nsk3-v9n7','gebiedregeling':'qtex-qwd8','regeling':'yefi-qfiq','tijdvak':'ixf8-gtwq','tarief':'534e-5vdg'}
D=os.path.join(WERK,'parkeren')
def haal(naam):
    p=os.path.join(D,naam+'.json'); uit=[]; off=0
    while True:
        q=urllib.parse.urlencode({'areamanagerid':'599','$limit':5000,'$offset':off})
        with urllib.request.urlopen(RDW+SETS[naam]+'.json?'+q,timeout=120) as r: rij=json.load(r)
        uit+=rij; off+=len(rij)
        if len(rij)<5000: break
    json.dump(uit,open(p,'w',encoding='utf8')); return uit
def dt(s): s=re.sub(r'\D','',s or '')[:8]; return s[:4]+'-'+s[4:6]+'-'+s[6:8] if len(s)==8 else ''
def wkt(t):
    ps=[]
    for ring in re.findall(r'\(\(([^()]+)\)',t or ''):
        ps.append([tuple(map(float,c.split())) for c in ring.split(',')])
    return ps
def main():
    os.makedirs(D,exist_ok=True)
    R={n:haal(n) for n in SETS}; print({n:len(v) for n,v in R.items()})
    naam={g['areaid']:g.get('areadesc','') for g in R['gebied']}
    geo={}
    for g in sorted(R['geometrie'],key=lambda g:g.get('startdatearea','')):
        geo[g['areaid']]=g.get('areageometryastext')   # nieuwste contour
    regs=collections.defaultdict(list)
    for r in R['gebiedregeling']: regs[r['areaid']].append((dt(r['startdatearearegulation']),dt(r['enddatearearegulation']),r['usageid'],r['regulationid']))
    tv=collections.defaultdict(list)
    for t in R['tijdvak']: tv[t['regulationid']].append(t)
    tar=collections.defaultdict(list)
    for t in R['tarief']: tar[t['farecalculationcode']].append(t)
    def uurtarief(regid,peil):
        for t in tv.get(regid,[]):
            if t.get('daytimeframe')!='WOENSDAG' or not (dt(t['startdatetimeframe'])<=peil<=dt(t['enddatetimeframe'])): continue
            if not (int(t.get('starttimetimeframe') or 0)<=1200<int(t.get('endtimetimeframe') or 0)): continue
            parts=[p for p in tar.get(t.get('farecalculationcode'),[]) if dt(p['startdatefarepart'])<=peil<=dt(p['enddatefarepart']) and float(p.get('startdurationfarepart') or 0)==0]
            if parts:
                p=parts[0]; stap=float(p.get('stepsizefarepart') or 0)
                return round(float(p['amountfarepart'])*60/stap,2) if stap else None
        return None
    jaren=[str(j) for j in range(2016,2027)]
    peil={j:(j+'-07-01' if j<'2026' else STAND) for j in jaren}
    zones=[];centra=[]
    for aid,g in geo.items():
        rings=wkt(g)
        if not rings: continue
        rr=[[K.xy(x,y) for x,y in r] for r in rings]
        d=''.join('M'+' '.join(f'{x:.1f},{y:.1f}' for x,y in r)+'Z' for r in rr)
        per={}
        for j in jaren:
            akt=[x for x in regs.get(aid,[]) if x[2]=='BETAALDP' and x[0]<=peil[j]<=x[1]]
            if akt: per[j]=uurtarief(akt[0][3],peil[j]) or 0
        toekomst=sorted(x[0] for x in regs.get(aid,[]) if x[2]=='BETAALDP' and x[0]>STAND)
        eerste=min((x[0] for x in regs.get(aid,[]) if x[2]=='BETAALDP'),default='')
        cx=sum(x for r in rr for x,_ in r)/sum(len(r) for r in rr); cy=sum(y for r in rr for _,y in r)/sum(len(r) for r in rr)
        centra.append((sum(x for r in rings for x,_ in r)/sum(len(r) for r in rings),sum(y for r in rings for _,y in r)/sum(len(r) for r in rings)))
        zones.append({'id':aid,'naam':naam.get(aid,''),'d':d,'x':round(cx),'y':round(cy),'jaren':per,'eerste':eerste,'gepland':toekomst[0] if toekomst else ''})
    # wijken: al betaald parkeren (een zone van nu ligt in de wijk), gepland volgens het Kader 2026 (heel de stad behalve de kleine kernen), of uitgezonderd
    import gebieden as GB, bag_straten as BS
    rows,WW,wijk_b,b_wijk,wijk_g=GB.hierarchie()
    B=json.load(open(os.path.join(WERK,'kaart','buurten_2024.json'),encoding='utf8'))['features']; poly={f['properties']['buurtcode']:BS.ringen(f['geometry']) for f in B}
    nu=[c for z,c in zip(zones,centra) if STAND in [peil['2026']] and '2026' in z['jaren']]
    UIT={'hoek-van-holland','rozenburg','pernis'}; UITW={'heijplaat'}
    wstat={}
    for g,ws in WW.items():
        for w in ws:
            heeft=any(BS.binnen(x,y,r) for x,y in nu for b in wijk_b[w] for r in poly.get(b,[]))
            wstat[w]='betaald' if heeft else ('uitgezonderd' if g in UIT or w in UITW else 'gepland')
    stat={j:{'zones':sum(1 for z in zones if j in z['jaren']),'tarief':sorted(v for z in zones for jj,v in z['jaren'].items() if jj==j and v)} for j in jaren}
    stat={j:{'zones':s['zones'],'mediaan':(s['tarief'][len(s['tarief'])//2] if s['tarief'] else None),'max':(s['tarief'][-1] if s['tarief'] else None)} for j,s in stat.items()}
    out={'stand':STAND,'bron':'RDW Open Data Parkeren (gebiedsbeheerder Rotterdam), opgehaald '+datetime.date.today().isoformat(),'jaren':jaren,'zones':zones,'stat':stat,'wijken':wstat,
         'kader':{'tekst':"Volgens het Kader voor de invoering van betaald parkeren (raadsvoorstel, september 2026) en het coalitieakkoord komt er gefaseerd betaald parkeren in heel Rotterdam, behalve in de kleine kernen Hoek van Holland, Rozenburg, Pernis en Heijplaat.",
                  'url':'https://gemeenteraad.rotterdam.nl/Reports/Item/8e50c477-d4b0-4410-a0bc-9baa957af4f8'}}
    json.dump(out,open(os.path.join(DOCS,'d','parkeren-kaart.json'),'w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
    print(len(zones),'zones',{j:(s['zones'],s['mediaan']) for j,s in stat.items()},'gepland',sum(1 for z in zones if z['gepland']),collections.Counter(wstat.values()))
if __name__=='__main__': main()
