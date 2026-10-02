# Zet de opgehaalde iBabs-stukken om naar docs/data/ibabs/stukken.zst voor het tabblad "Officiële stukken".
# Invoer: WERK/ibabs/lijsten.json en (waar aanwezig) WERK/ibabs/items_<soort>.jsonl. Alleen stukken vanaf 2018.
# Rij: [soort, datum, titel, wie, status, statustekst, tekst, itemId, bb-nummer]
#   status: 0 onbekend/geen, 1 aangenomen, 2 verworpen, 3 ingetrokken/aangehouden, 4 open (toezegging/motie niet afgedaan), 5 afgedaan
import json,os,re,zstandard,collections
from paden import WERK,DOCS
WIJK=[('ongevraagd','Ongevraagd wijkraadadvies'),('wijkakkoorden','Wijkakkoord of wijkplan'),('reacties','Collegereactie op wijkplan'),('verslagen','Wijkverslag')]
SOORTEN=[('toezeggingen','Toezegging'),('moties','Motie'),('amendementen','Amendement'),('initiatiefvoorstellen','Initiatiefvoorstel'),
         ('raadsvoorstellen','Raadsvoorstel'),('besluiten','Collegebesluit'),('brieven','Collegebrief'),('schriftelijke_vragen','Schriftelijke vragen'),('wijkraadadviezen','Wijkraadadvies')]
def iso(d):
    m=re.match(r'\s*(\d\d)-(\d\d)-(\d{4})',d or '')
    return f'{m.group(3)}-{m.group(2)}-{m.group(1)}' if m else ''
def schoon(t,n=None):
    t=re.sub(r'[ \t]+',' ',(t or '').replace('\r','')); t=re.sub(r'\n\s*\n+','\n',t).strip()
    return t[:n] if n else t
def debat_index():
    """Geeft een functie (titel, trefwoord, vanaf) -> datums van raadsvergaderingen waarin de titel letterlijk valt."""
    import glob
    norm=lambda s:' '+re.sub(r'[^a-z0-9à-ÿ]+',' ',s.lower())+' '
    dz=zstandard.ZstdDecompressor(); per={}
    for p in glob.glob(os.path.join(DOCS,'data','raad','*.zst')):
        Y=json.loads(dz.decompress(open(p,'rb').read(),max_output_size=10**9))
        for i,tx in enumerate(Y['s']['t']):
            if Y['s']['k'][i] in(0,4):
                n=norm(tx)
                for kw in(' rekenkamer',' ombudsman'):
                    if kw in n: per.setdefault(kw,{}).setdefault(Y['M'][Y['s']['m'][i]][0],[]).append(n)
    def dichtbij(seg,n,kw):
        ks=[m.start() for m in re.finditer(re.escape(kw),seg)]
        p=seg.find(n)
        while p>=0:
            if any(abs(p-k)<400 for k in ks): return True
            p=seg.find(n,p+1)
        return False
    def f(titel,kw,vanaf):
        # alleen als de titel binnen ~400 tekens van het woord rekenkamer/ombudsman valt, en pas na publicatie
        n=norm(titel)
        if len(n.split())<2 and len(n)<12: return []   # te korte titels geven ruis
        return sorted(d for d,segs in per.get(kw,{}).items() if d>=vanaf and any(n in s and dichtbij(s,n,kw) for s in segs))
    return f
def main():
    L=json.load(open(os.path.join(WERK,'ibabs','lijsten.json'),encoding='utf8'))
    rows=[]; st=collections.Counter()
    for k,(naam,label) in enumerate(SOORTEN):
        det={}
        p=os.path.join(WERK,'ibabs',f'items_{naam}.jsonl')
        if os.path.exists(p):
            for l in open(p,encoding='utf8'):
                d=json.loads(l); det[d['id']]=d
        for r in L[naam]:
            datum=iso(r.get('registrationdate') or r.get('datumbesluit'))
            if datum<'2018': continue
            d=det.get(r['DT_RowId'],{}); D=d.get('detail',{})
            wie=r.get('partij') or r.get('portefeuillehouder') or r.get('portefeuillehouder2') or r.get('raadslid') or ''
            if r.get('raadslid') and r.get('partij'): wie=f"{r['partij']} ({r['raadslid']}{', '+r['medeondertekenaars'] if r.get('medeondertekenaars') else ''})"
            if naam=='toezeggingen' and r.get('commissie'): wie=f"{wie.strip()} · {r['commissie']}"
            uit=(r.get('uitslag') or D.get('Uitslag') or '').strip().lower()
            af=D.get('Afgedaan')
            status=0; stx=''
            if uit.startswith('aangenomen') or uit.startswith('aanvaard'): status=1
            elif uit.startswith('verworpen'): status=2
            elif uit.startswith(('ingetrokken','aangehouden')): status=3
            if uit: stx=uit
            if naam in('toezeggingen','moties') and af is not None and (naam=='toezeggingen' or status==1):
                status=5 if af else 4
                stx=(stx+' · ' if stx else '')+('afgedaan'+(' '+D.get('Datum afgedaan') if D.get('Datum afgedaan') else '') if af else 'nog niet afgedaan'+(' · verwacht '+D['Verwachte datum afdoening'] if D.get('Verwachte datum afdoening') else ''))
            if naam=='schriftelijke_vragen': stx='beantwoord '+r['datecompleted'][:10] if r.get('datecompleted') else 'nog niet beantwoord'
            tekst=schoon(D.get('Omschrijving'))
            if D.get('Stand van zaken'): tekst+='\nStand van zaken: '+schoon(D['Stand van zaken'])
            if d.get('tekst'): tekst+=('\n\n' if tekst else '')+schoon(d['tekst'],20000)
            rows.append([k,datum,schoon(r.get('title')),schoon(wie),status,stx,tekst,r['DT_RowId'],r.get('externalid') or ''])
            st[naam]+=1; st[naam+'_detail']+=bool(D); st[naam+'_tekst']+=bool(d.get('tekst'))
    # stap 5: Rekenkamer Rotterdam en Ombudsman Rotterdam-Rijnmond (extern.py); itemId is hier een volledige url
    soorten=[s[1] for s in SOORTEN]+['Rekenkamerrapport','Ombudsman']+[x[1] for x in WIJK]
    deb=debat_index()
    for k,naam in ((len(SOORTEN),'rekenkamer'),(len(SOORTEN)+1,'ombudsman')):
        p=os.path.join(WERK,'extern',naam+'.json')
        if not os.path.exists(p): continue
        for x in json.load(open(p,encoding='utf8')):
            tx=re.sub(r'^'+re.escape(x['titel'])+r'\s*(Rekenkamer Rotterdam, \d\d-\d\d-\d{4})?\s*','',x['tekst'].strip())
            stx='lopend onderzoek' if x.get('status')=='lopend' else (x.get('soort','').lower())
            wie=x.get('domein') or ''
            d=deb(x['titel'],' '+naam,x['datum']) if x.get('status')!='lopend' else []
            if d: stx=(stx+' · ' if stx else '')+'genoemd in '+str(len(d))+' raadsvergadering'+('en' if len(d)>1 else '')
            rows.append([k,x['datum'],x['titel'],wie,0,stx,schoon(tx),x['url'],'',d])
            st[naam]+=1; st[naam+'_debat']+=bool(d)
    # stap 6: wijkraden (wijkraden.py), url naar wijkraad.rotterdam.nl
    p=os.path.join(WERK,'ibabs','wijk.jsonl')
    if os.path.exists(p):
        ki={x[0]:len(SOORTEN)+2+i for i,x in enumerate(WIJK)}
        for l in open(p,encoding='utf8'):
            try: d=json.loads(l)
            except Exception: continue
            r=d['lijst']; D=d.get('detail',{}); datum=iso(r.get('registrationdate'))
            if datum<'2018': continue
            wie=r.get('Wijk') or ''
            if r.get('wethouder'): wie+=' · '+r['wethouder']
            stx=''
            if d['soort']=='ongevraagd': stx='beantwoord '+r['datumantwoord'][:10] if r.get('datumantwoord') else 'nog niet beantwoord'
            tekst=schoon(D.get('Omschrijving'))
            if d.get('tekst'): tekst+=('\n\n' if tekst else '')+schoon(d['tekst'],20000)
            rows.append([ki[d['soort']],datum,schoon(r.get('title')),wie,0,stx,tekst,'https://wijkraad.rotterdam.nl/Reports/Item/'+d['id'],''])
            st['wijk_'+d['soort']]+=1; st['wijk_tekst']+=bool(d.get('tekst'))
    rows.sort(key=lambda x:x[1],reverse=True)
    out={'soorten':soorten,'s':rows}
    raw=json.dumps(out,ensure_ascii=False,separators=(',',':')).encode('utf8')
    z=zstandard.ZstdCompressor(level=19).compress(raw)
    os.makedirs(os.path.join(DOCS,'data','ibabs'),exist_ok=True)
    open(os.path.join(DOCS,'data','ibabs','stukken.zst'),'wb').write(z)
    import time; stand=time.strftime('%d-%m-%Y',time.localtime(os.path.getmtime(os.path.join(WERK,'ibabs','lijsten.json'))))
    json.dump({'stand':stand,'z':len(z),'raw':len(raw),'n':len(rows),'per':{s[1]:st[s[0]] for s in SOORTEN}},open(os.path.join(DOCS,'data','ibabs','meta.json'),'w',encoding='utf8'),ensure_ascii=False)
    print(len(rows),'stukken',round(len(raw)/1e6,1),'MB raw',round(len(z)/1e6,2),'MB zst',dict(st))
if __name__=='__main__': main()
