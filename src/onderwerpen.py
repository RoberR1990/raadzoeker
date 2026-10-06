# Concrete onderwerpen voor holistische AI-samenvattingen (fijner dan de 41 thema's).
# Per onderwerp: naam, zoekpatronen (regex op gevouwen tekst, woordbegin). Telling van bronnen sinds 2022:
#   python src/onderwerpen.py   -> WERK/teksten/onderwerpen_telling.json en een tabel
import json,os,re,glob,collections,zstandard
import teksten as T
from paden import WERK,DOCS
O=[
 ('Deelscooters en deelfietsen',[r'deelscooter',r'deelfiets',r'deelmobiliteit',r'deelvervoer']),
 ('Parkeeroverlast en parkeerdruk',[r'parkeeroverlast',r'parkeerdruk',r'foutparkeren',r'fout geparkeerd',r'parkeerplaatsen']),
 ('Betaald parkeren en parkeervergunningen',[r'betaald parkeren',r'parkeervergunning',r'parkeertarie',r'bewonersvergunning']),
 ('Fietsparkeren en weesfietsen',[r'fietsparkeren',r'fietsenstalling',r'weesfiets',r'fietsparkeer']),
 ('Verkeersveiligheid en 30 km/u',[r'verkeersveilig',r'30 ?km',r'snelheidsovertred',r'verkeersongeval']),
 ('Zero-emissiezone en luchtkwaliteit',[r'zero.?emissie',r'milieuzone',r'luchtkwaliteit',r'fijnstof',r'stikstofdioxide']),
 ('Laadpalen',[r'laadpa(a|l)',r'laadinfra']),
 ('Openbaar vervoer en RET',[r'\bret\b',r'buslijn',r'tramlijn',r'ov.?verbinding',r'openbaar vervoer']),
 ('Afval, zwerfvuil en grofvuil',[r'zwerfafval',r'zwerfvuil',r'grofvuil',r'afvalinzameling',r'bijplaatsing',r'ondergrondse container',r'dumping']),
 ('Ratten en ongedierte',[r'\bratten',r'rattenoverlast',r'ongedierte']),
 ('Vuurwerk en jaarwisseling',[r'vuurwerk',r'jaarwisseling',r'oud en nieuw']),
 ('Explosies bij woningen en bedrijven',[r'explosie(?!v)',r'aanslagen? op (woningen|panden|bedrijven)',r'cobra']),   # niet: explosieven
 ('Ondermijning en drugscriminaliteit',[r'ondermijning',r'drugscriminaliteit',r'cocaine',r'drugshandel']),
 ('Cameratoezicht',[r'cameratoezicht',r'camera.?s']),
 ('Jongerenoverlast en jeugdcriminaliteit',[r'jongerenoverlast',r'jeugdcriminaliteit',r'jeugdgroep',r'messen',r'wapenbezit']),
 ('Horeca, terrassen en nachtleven',[r'terras',r'nachtleven',r'horecaoverlast',r'sluitingstijd']),
 ('Lachgas',[r'lachgas']),
 ('Evenementen en overlast',[r'evenementenbeleid',r'evenementenoverlast',r'geluidsoverlast evenement',r'evenementenvergunning']),
 ('Arbeidsmigranten',[r'arbeidsmigrant']),
 ('Kamerverhuur en woningdelen',[r'kamerverhuur',r'verkamer',r'woningdel',r'woningvorming']),
 ('Goed verhuurderschap en huisjesmelkers',[r'verhuurderschap',r'goed huren',r'huisjesmelk',r'malafide verhuur',r'verhuurvergunning']),
 ('Sociale huur en sloop/nieuwbouw',[r'sociale huur',r'woningcorporatie',r'sloop',r'tweebos']),
 ('Middenhuur en betaalbaar wonen',[r'middenhuur',r'betaalbare (woningen|huur)',r'wet betaalbare huur',r'opkoopbescherming']),
 ('Dakloosheid en daklozenopvang',[r'dakloos',r'daklozen',r'nachtopvang',r'maatschappelijke opvang']),
 ('Asielopvang en statushouders',[r'asielzoeker',r'azc',r'statushouder',r'spreidingswet',r'asielopvang']),
 ('Schulden en armoede',[r'schulden',r'schuldhulp',r'armoede',r'minimabeleid']),
 ('Energiearmoede en isolatie',[r'energiearmoede',r'isolatie',r'isoleren',r'energierekening']),
 ('Warmtenet en aardgasvrij',[r'warmtenet',r'aardgasvrij',r'warmtetransitie']),
 ('Hittestress en vergroening',[r'hittestress',r'vergroen',r'tegels eruit',r'klimaatadaptatie',r'groene daken']),
 ('Bomenkap en bomen',[r'bomenkap',r'\bkap van',r'bomen']),
 ('Feyenoord City en stadion',[r'feyenoord city',r'stadion',r'de kuip']),
 ('Museum Boijmans Van Beuningen',[r'boijmans']),
 ('Rotterdam The Hague Airport',[r'rotterdam the hague airport',r'\brtha\b',r'vliegveld',r'luchthaven']),
 ('Jeugdhulp',[r'jeugdhulp',r'jeugdzorg']),
 ('Wmo en hulp bij het huishouden',[r'\bwmo\b',r'hulp bij het huishouden',r'huishoudelijke hulp']),
 ('Doelgroepenvervoer',[r'doelgroepenvervoer',r'wmo.?vervoer']),
 ('Kansengelijkheid en onderwijs',[r'kansengelijkheid',r'laaggeletterd',r'onderwijsachterstand',r'schooluitval']),
 ('Discriminatie en racisme',[r'discriminatie',r'racisme',r'stagediscriminatie']),
 ('Prostitutie en mensenhandel',[r'prostitutie',r'mensenhandel',r'sekswerk']),
 ('Coffeeshops en drugsbeleid',[r'coffeeshop',r'softdrugs',r'drugsbeleid']),
 ('Walstroom en haven-uitstoot',[r'walstroom',r'cruiseschip',r'cruiseterminal']),
 ('Wijkraden en participatie',[r'participatie',r'wijkraden',r'bewonersinitiatie']),
 ('Handhaving en toezicht',[r'handhav',r'boa\b',r"boa's",r'toezichthouder',r'stadswacht',r'bestuurlijke boete',r'bestuurlijke strafbeschikking',r'last onder dwangsom',r'bodycam']),   # voorbeelddossier, zie showcase.py
]
# Thema's dwars door de organisatie (5-10-2026, herzien): scherper dan de oude thema's uit themes.py, zodat ze weinig overlappen
# (gemeten met src/thema_overlap.py). AI, data en digitalisering samengevoegd; geen algemene woorden als 'monitor' of 'evaluatie'.
DWARS=[
 ('Digitalisering, data en AI',[r'kunstmatige intelligentie',r'artificial intelligence',r'ai\b',r'algoritme',r'chatgpt',r'taalmodel',r'machine learning',r'risicomodel',r'risicoprofiel',
   r'privacy',r'avg\b',r'persoonsgegevens',r'datalek',r'gegevensbescherming',r'datagedreven',r'open data',r'digitalis',r'ict\b',r'cyber',r'glasvezel',r'smart city'],
   [('AI en algoritmen',[r'kunstmatige intelligentie',r'artificial intelligence',r'ai\b',r'algoritme',r'chatgpt',r'taalmodel',r'machine learning',r'risicomodel',r'risicoprofiel']),
    ('Privacy en data',[r'privacy',r'avg\b',r'persoonsgegevens',r'datalek',r'gegevensbescherming',r'datagedreven',r'open data']),
    ('ICT en digitale dienstverlening',[r'digitalis',r'ict\b',r'cyber',r'glasvezel',r'smart city'])]),
 ('Participatie en inspraak',[r'inspraak',r'participatietraject',r'participatieproces',r'participatieaanpak',r'burgerparticipatie',r'bewonersparticipatie',r'referendum',r'burgerberaad',r'burgerpanel',r'bewonersinitiatie',r'right to challenge'],[]),
 ('Discriminatie en inclusie',[r'discriminatie',r'racisme',r'racistisch',r'inclusie',r'diversiteit',r'emancipatie',r'lhbt',r'homoseksu',r'transgender'],[]),
 ('Integriteit en transparantie',[r'integriteit',r'geheimhouding',r'woo\b',r'transparant',r'klokkenluider',r'belangenverstrengeling',r'nevenfuncties'],[]),
 ('Inkoop, aanbesteding en subsidie',[r'aanbested',r'inkoop',r'subsidie',r'leverancier',r'contractmanagement'],[]),
 ('Rekenkamer, ombudsman en verantwoording',[r'rekenkamer',r'ombudsman',r'accountant',r'audit',r'doelmatigheid',r'jaarverslag',r'verantwoording'],[]),
 ('Innovatie en experimenten',[r'innovatie',r'innovatief',r'experiment',r'proeftuin',r'pilot',r'start-?up'],[]),
 ('Regio en Rijk',[r'metropoolregio',r'mrdh\b',r'provincie',r'rijksoverheid',r'vng\b',r'kabinet',r'het rijk\b'],[]),
]
def rx(pp): return re.compile(r'\b(?:'+'|'.join(pp)+r')')
# Thema (themes.py) waaronder elk onderwerp valt; niet genoemde onderwerpen zijn geschrapt (te weinig bronnen of te breed).
THEMA={'Deelscooters en deelfietsen':'Mobiliteit & verkeer','Parkeeroverlast en parkeerdruk':'Parkeren','Betaald parkeren en parkeervergunningen':'Parkeren',
 'Fietsparkeren en weesfietsen':'Mobiliteit & verkeer','Verkeersveiligheid en 30 km/u':'Mobiliteit & verkeer','Zero-emissiezone en luchtkwaliteit':'Mobiliteit & verkeer',
 'Openbaar vervoer en RET':'Mobiliteit & verkeer','Afval, zwerfvuil en grofvuil':'Buitenruimte & afval','Ratten en ongedierte':'Buitenruimte & afval',
 'Vuurwerk en jaarwisseling':'Veiligheid & handhaving','Explosies bij woningen en bedrijven':'Veiligheid & handhaving','Ondermijning en drugscriminaliteit':'Veiligheid & handhaving',
 'Cameratoezicht':'Veiligheid & handhaving','Jongerenoverlast en jeugdcriminaliteit':'Veiligheid & handhaving','Lachgas':'Veiligheid & handhaving',
 'Horeca, terrassen en nachtleven':'Economie & haven','Evenementen en overlast':'Cultuur, sport & evenementen','Arbeidsmigranten':'Werk & inkomen',
 'Kamerverhuur en woningdelen':'Wonen','Goed verhuurderschap en huisjesmelkers':'Wonen','Sociale huur en sloop/nieuwbouw':'Wonen','Middenhuur en betaalbaar wonen':'Wonen',
 'Dakloosheid en daklozenopvang':'Zorg, welzijn & jeugd','Asielopvang en statushouders':'Asiel & migratie','Schulden en armoede':'Werk & inkomen',
 'Energiearmoede en isolatie':'Energie & klimaat','Warmtenet en aardgasvrij':'Energie & klimaat','Hittestress en vergroening':'Buitenruimte & afval','Bomenkap en bomen':'Buitenruimte & afval',
 'Feyenoord City en stadion':'Bouwen & ruimte','Museum Boijmans Van Beuningen':'Cultuur, sport & evenementen','Rotterdam The Hague Airport':'Economie & haven',
 'Jeugdhulp':'Zorg, welzijn & jeugd','Wmo en hulp bij het huishouden':'Zorg, welzijn & jeugd','Doelgroepenvervoer':'Zorg, welzijn & jeugd',
 'Kansengelijkheid en onderwijs':'Onderwijs','Discriminatie en racisme':'Discriminatie & inclusie','Walstroom en haven-uitstoot':'Economie & haven',
 'Handhaving en toezicht':'Veiligheid & handhaving'}
def actief(): return [(n,pp) for n,pp in O if n in THEMA]
def termen(pp):
    """Leesbare zoektermen (voor links en markering) uit de patronen: alleen de eenvoudige."""
    return '|'.join(p.replace('\\b','') for p in pp if re.fullmatch(r'(\\b)?[a-z0-9 ]+',p))
def main():
    R=[(n,rx(pp)) for n,pp in O]
    tel={n:collections.Counter() for n,_ in O}
    groep=lambda s:{'Motie':'motie','Amendement':'motie','Toezegging':'toez','Schriftelijke vragen':'sv','Raadsvoorstel':'rv','Initiatiefvoorstel':'rv','Collegebrief':'brief',
                    'Rekenkamerrapport':'rk','Ombudsman':'rk'}.get(s,'wijk' if s.startswith(('Wijk','Ongevraagd','Collegereactie')) else 'ov')
    for key,soort,datum,titel,wie,url,t in T.bronnen():
        if (datum or '')<'2022': continue
        f=T.fold((titel or '')+' '+t[:30000])
        for n,r in R:
            if len(r.findall(f))>=2 or r.search(T.fold(titel or '')): tel[n][groep(soort)]+=1
    dz=zstandard.ZstdDecompressor()
    for p in glob.glob(os.path.join(DOCS,'data','raad','202[2-6].zst'))+glob.glob(os.path.join(DOCS,'data','commissies','202[2-6].zst')):
        Y=json.loads(dz.decompress(open(p,'rb').read(),max_output_size=10**9))
        for i,t in enumerate(Y['s']['t']):
            if Y['s']['k'][i] not in(0,4) or not t: continue
            f=T.fold(t)
            for n,r in R:
                if r.search(f): tel[n]['debat']+=1
    json.dump({n:dict(c) for n,c in tel.items()},open(os.path.join(WERK,'teksten','onderwerpen_telling.json'),'w',encoding='utf8'),ensure_ascii=False,indent=0)
    k='debat motie toez sv rv brief rk wijk'.split()
    print('onderwerp'.ljust(42)+''.join(x.rjust(7) for x in k))
    for n,_ in O: print(n[:41].ljust(42)+''.join(str(tel[n][x]).rjust(7) for x in k))
if __name__=='__main__': main()
