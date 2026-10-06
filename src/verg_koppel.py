# Vergadersamenvattingen verrijken en ontsluiten (geen AI): per agendapunt tijdvak in de video, links naar dossiers
# (domein, onderwerp, thema, gebied), alinea's in de korte versie; daarna de zoek- en dossierbestanden voor de site.
#   python src/verg_koppel.py   -> herbouwt docs/ontwerp/verg/zoek.json en koppel.json uit alle verg/<id8>.json
# verrijk(out, B) wordt aangeroepen door verg_check.py vóór het wegschrijven.
import json,os,re,glob,unicodedata
from paden import DOCS,WERK
import onderwerpen as O
VD=os.path.join(DOCS,'ontwerp','verg')
def fold(s): return ''.join(c for c in unicodedata.normalize('NFD',(s or '').lower()) if unicodedata.category(c)!='Mn')
_IX=None
def ix():
    global _IX
    if _IX is None:
        d=json.load(open(os.path.join(DOCS,'ontwerp','d','index.json'),encoding='utf8'))['d']
        naar={(x['soort'],x['naam']):x for x in d}
        dom=[x for x in d if x['soort']=='domein']; geb=[x for x in d if x['soort']=='gebied']
        ond=[(naar[('onderwerp',n)],O.rx(pp)) for n,pp in O.actief() if ('onderwerp',n) in naar]
        thm=[(naar[('thema',n)],O.rx(pp)) for n,pp,_ in O.DWARS if ('thema',n) in naar]
        from ontwerp_data import zload
        m=zload(os.path.join(DOCS,'data','debat','meta.zst'))
        _IX=dict(park=naar.get(('onderwerp','Parkeren')),dom={x['slug']:x for x in dom},domlijst=m['dom'],geblijst=m['geb'],geb={x['naam']:x for x in geb},ond=ond,thm=thm)
    return _IX
def dossiers(titel,body,dom,gebmask):
    I=ix(); uit=[]; t=fold(titel); b=fold(body)
    def neem(x,soort): uit.append({'slug':x['slug'],'naam':x['naam'],'soort':soort})
    kand=[]
    for x,r in I['ond']:
        nt=len(r.findall(t)); nb=len(r.findall(b))
        if nt or nb>=3: kand.append((nt*10+nb,x))
    gekozen=[x for _,x in sorted(kand,key=lambda k:-k[0])[:2]]
    # parkeeronderwerpen: ook naar het voorbeelddossier Parkeren (met kaart, beloftes en stemgedrag)
    if any(O.THEMA.get(x['naam'])=='Parkeren' for x in gekozen) and I['park']: neem(I['park'],'onderwerp')
    for x in gekozen: neem(x,'onderwerp')
    for x,r in I['thm']:
        nt=len(r.findall(t)); nb=len(r.findall(b))
        eerste=fold(x['naam']).split()[0]
        if (nt or nb>=3) and not any(fold(u['naam']).split()[0]==eerste for u in uit): neem(x,'thema'); break
    if dom is not None and dom>=0:
        x=I['dom'].get(I['domlijst'][dom][0])
        if x: neem(x,'domein')
    g=[I['geblijst'][i] for i in range(len(I['geblijst'])) if gebmask&(1<<i)]
    for n in g:   # gebied alleen als het in de titel staat (in de tekst genoemd is te vaak bijzaak)
        x=I['geb'].get(n)
        if x and fold(n) in t: neem(x,'gebied')
    return uit
def start(vref):
    # beginmoment van de video (Company Webcast), zodat de site kloktijden kan tonen
    import urllib.request
    if not (vref or '').startswith('c:'): return None
    try:
        r=urllib.request.Request('https://sdk.companywebcast.com/players/'+vref[2:].replace('/','_')+'/info',headers={'User-Agent':'Mozilla/5.0'})
        return json.load(urllib.request.urlopen(r,timeout=30)).get('start')
    except Exception as e: print('geen starttijd video:',e); return None
def verrijk(out,B):
    out['start']=start(out.get('video'))
    u2ap={u:nr for nr,a in B.get('ap',{}).items() for u in a['u']}
    for a in out['agendapunten']:
        A=B.get('ap',{}).get(a.get('nr'),{})
        us=[B['u'][u] for u in A.get('u',[]) if u in B['u']]
        if us:
            a['van']=int(min(x['segs'][0][0] for x in us))
            a['tot']=int(max(x['segs'][-1][0]+len(x['segs'][-1][1].split())/2.5 for x in us))
            # netto spreektijd: gaten van meer dan 10 minuten (pauze, ander agendapunt tussendoor) tellen niet mee
            st=sorted({int(sg[0]) for x in us for sg in x['segs']}|{a['tot']})
            a['duur']=round(sum(d for d in (b-c for c,b in zip(st,st[1:])) if d<600)/60)
            a['pauze']=any(b-c>=900 for c,b in zip(st,st[1:]))
        body=' '.join([a.get('wat',''),a.get('uitkomst','')]+[x.get('punt','') for v in ('fracties','college') for x in a.get(v,[])])
        a['titel_off']=A.get('titel','')
        a['dossiers']=dossiers(A.get('titel','')+' '+a.get('titel',''),body,A.get('dom'),A.get('geb',0))
    # korte versie in 2-3 alinea's: ongeveer even groot, bij voorkeur knippen waar een ander agendapunt begint
    K=out['kort']; doel=max(2,-(-len(K)//3)); n=0; groot=0; vorig=None
    for z in K:
        ap=u2ap.get(str(z.get('u','')).lstrip('#U'))
        if groot and ((groot>=doel and ap!=vorig) or groot>=doel+1): n+=1; groot=0
        z['alinea']=n; z['ap']=ap; groot+=1; vorig=ap
    return out
# ---- iBabs: welke stukken hangen aan welk agendapunt, en waar werden ze nog meer besproken (tijdlijn) ----
MND={m:i+1 for i,m in enumerate(['januari','februari','maart','april','mei','juni','juli','augustus','september','oktober','november','december'])}
AP=re.compile(r'(Gemeenteraad|Commissie [^\n]*?) (20\d\d)\s*\n\(([\d.]*)\s*([^\n]*)\)\s*\n\w+ (\d+) (\w+)')
SOORT={'moties':'Motie','amendementen':'Amendement','raadsvoorstellen':'Raadsvoorstel','initiatiefvoorstellen':'Initiatiefvoorstel','brieven':'Brief','toezeggingen':'Toezegging'}
def orgnorm(s): return re.sub(r'\s+',' ',re.sub(r'\(.*?\)|\b20\d\d\b|^commissie ','',fold(s))).strip()
def momenten(a):
    uit=[]
    for org,j,nr,tit,dag,mnd in AP.findall(a if isinstance(a,str) else ''):
        if mnd not in MND: continue
        raad=org=='Gemeenteraad'; nr=nr.strip('.')
        if (not raad and nr.startswith('1')) or (raad and re.search(r'mededeling|ingekomen|doorlopende lijst|vaststelling van de (agenda|notulen)',tit,re.I)) or not nr: continue
        uit.append((f'{j}-{MND[mnd]:02d}-{int(dag):02d}','Gemeenteraad' if raad else re.sub(r'\s*\(.*?\)','',org).strip(),nr,tit.strip()))
    return uit
def ibabs():
    I=[]
    for soort,naam in SOORT.items():
        p=os.path.join(WERK,'ibabs',f'items_{soort}.jsonl')
        if not os.path.exists(p): continue
        for l in open(p,encoding='utf8'):
            d=json.loads(l); D=d.get('detail') or {}; L=d.get('lijst') or {}
            m=momenten(D.get('Agendapunt',''))
            if m: I.append({'id':d['id'],'soort':naam,'titel':D.get('Titel') or L.get('title',''),'m':m,'uitslag':L.get('uitslag') or D.get('Uitslag') or '',
                            'partij':L.get('partij') or D.get('Partij') or ''})
    return I
STOP={'over','debat','raad','voor','naar','door','met','het','van','de','een','raadsvoorstel','collegebrief','bespreking','betrekken','bij','aangevraagd'}
def woordset(t): return {w for w in re.findall(r'[a-z0-9]{4,}',fold(t))}-STOP
def spoor(V,a,I,VERG,GEDAAN):
    """Stukken bij dit agendapunt (moties met uitslag, voorstellen, brieven) en alle andere momenten waarop die stukken op de agenda stonden."""
    org=orgnorm(V['naam']); ws=woordset(a.get('titel_off',''))
    raad=V['raad'] if 'raad' in V else V['naam']=='Gemeenteraad'
    # raad: agendapuntnummers kloppen met iBabs; commissies hebben in de debatindex soms grovere nummers, dan op titel
    def hier(mm): return mm[0]==V['datum'] and orgnorm(mm[1])==org and (mm[2]==a['nr'] or (not raad and ws and len(ws&woordset(mm[3]))/len(ws)>=.5))
    stukken=[x for x in I if any(hier(mm) for mm in x['m'])]
    mo=[[x['soort'],x['titel'],x['partij'],x['uitslag'],x['id']] for x in stukken if x['soort'] in ('Motie','Amendement')]
    st=[[x['soort'],x['titel'],x['id']] for x in stukken if x['soort'] not in ('Motie','Amendement','Toezegging')]
    tl={}
    for x in stukken:
        if x['soort'] in ('Motie','Amendement','Toezegging'): continue
        for mm in x['m']:
            k=(mm[0],orgnorm(mm[1]),mm[2]); 
            if k in tl: continue
            ag=VERG.get((mm[0],orgnorm(mm[1])))
            tl[k]=[mm[0],mm[1],mm[2],mm[3],(ag or '')[:8] if (ag or '')[:8] in GEDAAN else '',ag or '',1 if hier(mm) else 0]
    # subpunten ('2.04.01 Betrekken bij …') vallen onder hun hoofdpunt op dezelfde dag
    tl=sorted(x for x in tl.values() if not any(y is not x and y[0]==x[0] and y[1]==x[1] and x[2].startswith(y[2]+'.') for y in tl.values()))
    return {'mo':mo,'st':st[:12],'tl':tl if len(tl)>1 else []}
def indexen():
    Z=[];K={};S={}
    from ontwerp_data import zload
    m=zload(os.path.join(DOCS,'data','debat','meta.zst'))
    VERG={(v[0],orgnorm(v[2])):v[3] for v in m['verg'] if v[3]}
    GEDAAN={os.path.basename(p)[:8] for p in glob.glob(os.path.join(VD,'*.json'))}
    I=ibabs()
    for p in sorted(glob.glob(os.path.join(VD,'*.json'))):
        k=os.path.basename(p)[:-5]
        if len(k)!=8: continue
        v=json.load(open(p,encoding='utf8'))
        for a in v['agendapunten']:
            if not (a.get('wat') or '').strip(): continue
            tekst=' '.join([a.get('titel_off',''),a.get('wat',''),a.get('uitkomst','')]+[x.get('wie','')+' '+x.get('punt','') for f in ('fracties','college') for x in a.get(f,[])])
            Z.append([k,a['nr'],a['titel'],v['datum'],v['naam'],a.get('wat',''),tekst])
            sp=spoor(v,a,I,VERG,GEDAAN)
            if sp['mo'] or sp['st'] or sp['tl']: S[k+'|'+a['nr']]=sp
            for d in a.get('dossiers',[]):
                K.setdefault(d['slug'],[]).append([k,a['nr'],a['titel'],v['datum'],v['naam']])
    for L in K.values(): L.sort(key=lambda x:x[3],reverse=True)
    json.dump(Z,open(os.path.join(VD,'zoek.json'),'w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
    json.dump(K,open(os.path.join(VD,'koppel.json'),'w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
    json.dump(S,open(os.path.join(VD,'spoor.json'),'w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
    print('spoor.json',len(S),'agendapunten met stukken of tijdlijn')
    print('zoek.json',len(Z),'agendapunten; koppel.json',len(K),'dossiers')
if __name__=='__main__': indexen()
