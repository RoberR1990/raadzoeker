# Zet de opgehaalde iBabs-stukken om naar docs/data/ibabs/stukken.zst voor het tabblad "Officiële stukken".
# Invoer: WERK/ibabs/lijsten.json en (waar aanwezig) WERK/ibabs/items_<soort>.jsonl. Alleen stukken vanaf 2018.
# Rij: [soort, datum, titel, wie, status, statustekst, tekst, itemId, bb-nummer]
#   status: 0 onbekend/geen, 1 aangenomen, 2 verworpen, 3 ingetrokken/aangehouden, 4 open (toezegging/motie niet afgedaan), 5 afgedaan
import json,os,re,zstandard,collections
from paden import WERK,DOCS
SOORTEN=[('toezeggingen','Toezegging'),('moties','Motie'),('amendementen','Amendement'),('initiatiefvoorstellen','Initiatiefvoorstel'),
         ('raadsvoorstellen','Raadsvoorstel'),('besluiten','Collegebesluit'),('brieven','Collegebrief'),('schriftelijke_vragen','Schriftelijke vragen')]
def iso(d):
    m=re.match(r'\s*(\d\d)-(\d\d)-(\d{4})',d or '')
    return f'{m.group(3)}-{m.group(2)}-{m.group(1)}' if m else ''
def schoon(t,n=None):
    t=re.sub(r'[ \t]+',' ',(t or '').replace('\r','')); t=re.sub(r'\n\s*\n+','\n',t).strip()
    return t[:n] if n else t
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
    rows.sort(key=lambda x:x[1],reverse=True)
    out={'soorten':[s[1] for s in SOORTEN],'s':rows}
    raw=json.dumps(out,ensure_ascii=False,separators=(',',':')).encode('utf8')
    z=zstandard.ZstdCompressor(level=19).compress(raw)
    os.makedirs(os.path.join(DOCS,'data','ibabs'),exist_ok=True)
    open(os.path.join(DOCS,'data','ibabs','stukken.zst'),'wb').write(z)
    import time; stand=time.strftime('%d-%m-%Y',time.localtime(os.path.getmtime(os.path.join(WERK,'ibabs','lijsten.json'))))
    json.dump({'stand':stand,'z':len(z),'raw':len(raw),'n':len(rows),'per':{s[1]:st[s[0]] for s in SOORTEN}},open(os.path.join(DOCS,'data','ibabs','meta.json'),'w',encoding='utf8'),ensure_ascii=False)
    print(len(rows),'stukken',round(len(raw)/1e6,1),'MB raw',round(len(z)/1e6,2),'MB zst',dict(st))
if __name__=='__main__': main()
