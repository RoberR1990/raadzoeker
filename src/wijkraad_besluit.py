# Wijkraden zuinig (zonder AI): per vergadering de besluiten uit de besluitenlijst (bijlage in iBabs).
#   python src/wijkraad_besluit.py [vanaf=JJJJ-MM-DD]  -> docs/ontwerp/verg/wijkraden.json
# Procedurele punten en alles over insprekers vallen weg; bewonersinitiatieven worden samengevoegd tot één regel;
# namen na 'de heer/mevrouw' en rond 'inspreken' worden weggelakt (teksten.anoniem).
import json,os,re,sys,collections,datetime
from paden import WERK,DOCS
from teksten import anoniem
from gebieden import norm_raad
NR=re.compile(r'^\s*(\d{1,2}(?:\.[a-z0-9]{1,2})?)\s*$',re.M)
PROC=re.compile(r'^(update portefeuille|terugkoppeling|actielijst|inventarisatie|leeswijzer|vergaderschema|planning|opening|sluiting|rondvraag|vaststell(ing|en) (van )?(de )?(agenda|besluitenlijst|notulen|verslag)|mededeling|ter (besluitvorming|bespreking|informatie)|insprek|inspreker|inspreekster|inspreekrecht|actiepunten|pauze|bewonersinitiatieven$)',re.I)
INIT=re.compile(r'bewonersinitiatie',re.I)
VN=None
GEEN_NAAM={'Wijkraad','Dorpsraad','Voorzitter','Gemeente','Stadsbeheer','Politie','Iedereen','Niemand','Dit','Het','Deze','Die','Er','Men','Wijkmanager','Wijknetwerker','Wijkraadcoördinator','Secretaris','Bewoners','Bewoner','Ondernemers','Werkgroep','College','Wethouder','Burgemeester','Commissie','Raad','Stichting','Speeltuin','Ook','Daarnaast','Verder','Ieder','Elk','Elke','Wij','Zij','Hij','Ze','Iemand','Gebied','Rotterdam'}
def voornamen():
    # voornamen uit alle sprekers in raad en commissies, plus veelvoorkomende; gebruikt om namen in wijkraadteksten weg te lakken
    global VN
    if VN is None:
        from ontwerp_data import zload
        m=zload(os.path.join(DOCS,'data','debat','meta.zst'))
        VN={n.split()[0] for n in m['spk'] if n and n[0].isupper() and len(n.split())>1 and len(n.split()[0])>2}
        VN|={'Rick','Tim','Anton','Liesbeth','Alexander','Danny','Amaya','Theo','Rita','Ron','Astrid','Jan','Piet','Kees','Mohamed','Ahmed','Fatima','Sandra','Linda','Marco','Peter','Mark','Sanne','Lisa','Emma','Sophie','Daan','Thomas','Bas','Joost','Henk','Gerard','Ingrid','Monique','Ellen','Karin','Marieke','Esther'}
        VN-={'Rotterdam','Feyenoord','Kralingen','Noord','Zuid','West','Oost','Centrum','Hoek','Maas','Wijkraad','Dorpsraad'}
    return VN
GEEN_NAAM={'Wijkraad','Dorpsraad','Voorzitter','Gemeente','Stadsbeheer','Politie','Iedereen','Niemand','Dit','Het','Deze','Die','Er','Men','Wijkmanager','Wijknetwerker','Wijkraadcoördinator','Secretaris','Bewoners','Bewoner','Ondernemers','Werkgroep','College','Wethouder','Burgemeester','Commissie','Raad','Stichting','Speeltuin','Ook','Daarnaast','Verder','Ieder','Elk','Elke','Wij','Zij','Hij','Ze','Iemand','Gebied','Rotterdam','Iedere','Jongerenwerk','Organisatie','De','Een','Op','In','Na','Bij','Voor'}
def lak(t):
    vn=voornamen()
    t=re.sub(r'\b([A-Z][a-z]+)((?:\s+(?:van|de|der|den|el|al|ter|ten|op|het)){0,3}\s+[A-Z][a-zé]+)?\b',lambda m:'[naam]' if m.group(1) in vn else m.group(0),t)
    # voornaam als onderwerp van een actie ('Krista heeft …', 'Albert en Angelo spreken …')
    t=re.sub(r'\b([A-ZÖ][a-zë]{2,})(?=(?:,? (?:en )?[A-ZÖ][a-zë]{2,})* (?:gaat|gaan|spreekt|spreken|heeft|hebben|vraagt|vragen|neemt|nemen|stuurt|zorgt|zorgen|zal|zullen|mailt|belt|pakt|stelt|komt|informeert|checkt|maakt|geeft|geven)\b)',
             lambda m:m.group(0) if m.group(1) in GEEN_NAAM else '[naam]',t)
    t=re.sub(r'\b([A-ZÖ][a-zë]{2,})(?=(?:, [A-ZÖ][a-zë]{2,})*,? en \[naam\])',lambda m:m.group(0) if m.group(1) in GEEN_NAAM else '[naam]',t)   # 'Helen, Ömer en [naam]'
    return re.sub(r'\b(?:meneer|mevrouw|mevr\.|dhr\.|de heer)\s+(?:den |de |van )?[A-Z][a-z]+',lambda m:'[naam]',anoniem(t),flags=re.I)
def punten(t):
    delen=NR.split(t); uit=[]; init=[]; weg=set()
    for i in range(1,len(delen)-1,2):
        blok=delen[i+1]; b=re.split(r'\n\s*Besluit:\s*',blok,maxsplit=1)
        titel=lak(re.sub(r'\s+',' ',b[0]).strip()); besl=lak(re.sub(r'\s+',' ',b[1]).strip()) if len(b)>1 else ''
        nr=delen[i]
        # privacy: subpunten onder 'inspreekrecht' gaan over insprekers (bewoners): helemaal weglaten
        if any(nr.startswith(w+'.') for w in weg): continue
        if re.search(r'insprek|inspreker|inspreekster',titel,re.I): weg.add(nr); continue
        # namen van personen in de titel ('Voornaam Achternaam - …', '… namens …', 'met Voornaam Achternaam', '[naam]'): weglaten
        if re.search(r'\[naam\]|namens|\bmet [A-Z][a-z]+ (?:van |de |der |den )*[A-Z][a-z]+|^[A-Z][a-z]+ (?:(?:van|de|der|den)\s+)*[A-Z][a-z]+\s*[-–:&]',titel): continue
        besl=re.sub(r'(?:[Dd]e heer|[Mm]evrouw|[Mm]evr\.|[Dd]hr\.)\s*\[naam\][^.]*\.\s*','',besl)
        titel=re.sub(r'\s*Pagina \d+.*$','',titel)[:200]; besl=re.sub(r'\s*Pagina \d+\s*',' ',besl)[:600]
        if not titel or PROC.search(titel) or re.search(r'insprek|inspreker',titel,re.I): continue
        if INIT.search(besl) and len(titel)<90: init.append(titel); continue
        if not besl: continue
        uit.append([titel,besl])
    return uit,init
def main(vanaf):
    V={}
    for l in open(os.path.join(WERK,'wijk','wijkraadvergaderingen.jsonl'),encoding='utf8'):
        try: v=json.loads(l); V[v['id']]=v
        except Exception: pass
    W=json.load(open(os.path.join(DOCS,'ontwerp','wijken.json'),encoding='utf8'))['wijken']
    gebied={w['naam'].lower():w['gebied'] for w in W}
    per={}
    for l in open(os.path.join(WERK,'wijk','wijkraad_bijlagen.jsonl'),encoding='utf8'):
        d=json.loads(l)
        if not re.search(r'besluitenlijst',d.get('naam',''),re.I): continue
        t=d.get('tekst') or ''; m=re.search(r'Datum\s*\n?\s*(\d{2})-(\d{2})-(\d{4})',t)
        if not m: continue
        datum=f'{m.group(3)}-{m.group(2)}-{m.group(1)}'
        if datum<vanaf: continue
        raad=norm_raad(V.get(d['verg'],{}).get('raad',''))
        kop=re.search(r'(Wijkraad|Dorpsraad|Wijkcomit\w+)\s+([^\n(]+)',t)
        if kop: raad=norm_raad(kop.group(1)+' '+kop.group(2).strip())
        if not raad: continue
        pt,init=punten(t)
        if not pt and not init: continue
        # bijbehorende vergadering (zelfde raad, die datum) voor de link naar iBabs
        ag=next((k for k,v in V.items() if v.get('datum')==datum and norm_raad(v.get('raad',''))==raad),'')
        wnaam=re.sub(r'^(Wijkraad|Dorpsraad|Wijkcomit\w+)\s+','',raad)
        g=sorted({gebied[x] for x in gebied if x in wnaam.lower() or wnaam.lower() in x})
        per[(raad,datum)]={'raad':raad,'datum':datum,'agendaId':ag,'gebied':g,'p':pt,'init':init}
    L=sorted(per.values(),key=lambda x:(x['datum'],x['raad']),reverse=True)
    json.dump(L,open(os.path.join(DOCS,'ontwerp','verg','wijkraden.json'),'w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
    print(len(L),'wijkraadvergaderingen,',sum(len(x['p']) for x in L),'besluiten,',sum(len(x['init']) for x in L),'bewonersinitiatieven;',
          collections.Counter(bool(x['gebied']) for x in L))
if __name__=='__main__': main(sys.argv[1] if len(sys.argv)>1 else (datetime.date.today()-datetime.timedelta(days=730)).isoformat())
