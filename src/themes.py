# bron van waarheid voor thema's: [groep, [[naam, termen, [[subnaam, termen], ...]], ...]]
T=[
 ["Beleidsdomeinen",[
  ["Parkeren",'parkeer | parkeren',[
    ["Parkeernorm & nieuwbouw",'parkeernorm | parkeereis | parkeerbeleid'],
    ["Betaald parkeren & tarieven",'betaald parkeren | parkeertarie | parkeerbelasting | parkeergeld | venstertijd'],
    ["Vergunningen",'parkeervergunning | bewonersvergunning | bezoekersvergunning | bezoekersregeling | vergunninghouder'],
    ["Garages & P+R",'parkeergarage | "p+r" | transferium | stallingsgarage'],
    ["Handhaving & boetes",'naheffing | scanauto | parkeerboete | parkeercontrole | foutparkeer | wielklem'],
    ["Parkeerdruk & overlast",'parkeerdruk | parkeeroverlast | parkeerprobleem | parkeerplaats'],
    ["Fietsparkeren",'fietsparkeer | fietsenstalling | fietsnietje | weesfiets'],
    ["Laden & deelauto",'laadpaal | laadpalen | laadinfra | deelauto']]],
  ["Mobiliteit & verkeer",'verkeer | mobiliteit | fiets | openbaar vervoer | "metro" | "tram" | deelscooter | deelvervoer',[
    ["Fiets",'fietspad | fietser | fietsstraat | fietsbrug'],
    ["Openbaar vervoer",'openbaar vervoer | "ret" | "metro" | "tram" | buslijn | "ov"'],
    ["Verkeersveiligheid",'verkeersveilig | 30 km | snelheid | verkeersdrempel | schoolzone | verkeersongeval'],
    ["Deelvervoer",'deelscooter | deelfiets | deelvervoer | deelmobiliteit'],
    ["Autoverkeer & bereikbaarheid",'bereikbaarheid | file | milieuzone | zero-emissie | oeververbinding | a16']]],
  ["Wonen",'woning | huurder | woonvisie | corporatie | daklo | leegstand',[
    ["Sociale huur & corporaties",'sociale huur | corporatie | woonstad | vestia | havensteder | woonbron'],
    ["Betaalbaarheid & middenhuur",'betaalba | middenhuur | huurprij | huurverhoging'],
    ["Nieuwbouw & sloop",'nieuwbouw | sloop | woningbouw | tweebosbuurt'],
    ["Dak- en thuisloosheid",'daklo | thuisloos | nachtopvang | maatschappelijke opvang'],
    ["Verhuur & toezicht",'huisjesmelker | verhuurdervergunning | woonoverlast | opkoopbescherming | kamerverhuur'],
    ["Studenten & starters",'student | starter | jongerenhuisvesting']]],
  ["Bouwen & ruimte",'bestemmingsplan | omgevingsvisie | omgevingswet | omgevingsplan | gebiedsontwikkeling | stedenbouw | hoogbouw',[
    ["Bestemmings- & omgevingsplannen",'bestemmingsplan | omgevingsplan | omgevingswet | omgevingsvisie'],
    ["Gebiedsontwikkeling",'gebiedsontwikkeling | feyenoord city | merwe-vierhaven | "m4h" | rijnhaven | stadionpark'],
    ["Hoogbouw & verdichting",'hoogbouw | verdicht | woontoren'],
    ["Erfgoed & welstand",'monument | erfgoed | welstand']]],
  ["Buitenruimte & afval",'afval | container | buitenruimte | zwerfvuil | grofvuil | riolering | bomenkap | groenonderhoud',[
    ["Afval & containers",'afval | container | grofvuil | bijplaatsing | zwerfvuil'],
    ["Groen & bomen",'bomen | groenonderhoud | park | vergroen'],
    ["Riolering & water",'riolering | wateroverlast | grondwater | funderingen'],
    ["Spelen & speelplekken",'speeltuin | speelplek | speelruimte'],
    ["Ongedierte & honden",'ratten | hondenpoep | hondenbelasting | meeuwen']]],
  ["Energie & klimaat",'klimaat | energie | warmtenet | aardgas | duurzaam | co2 | stikstof | luchtkwaliteit',[
    ["Warmte & aardgasvrij",'warmtenet | aardgas | warmtebedrijf | warmtetransitie'],
    ["Energiearmoede & isolatie",'energiearmoede | isolatie | isoleren | energierekening | energietoeslag'],
    ["Luchtkwaliteit & stikstof",'luchtkwaliteit | stikstof | fijnstof | houtstook'],
    ["Klimaatadaptatie",'klimaatadaptatie | hittestress | wateroverlast | weerwoord'],
    ["Opwek & netcongestie",'zonnepanelen | windmolen | netcongestie | waterstof']]],
  ["Veiligheid & handhaving",'veiligheid | handhav | politie | cameratoezicht | explosie | fouilleren | overlast | ondermijning',[
    ["Explosies & geweld",'explosie | wapen | steekpartij | schietpartij | messen'],
    ["Ondermijning & drugs",'ondermijning | drugs | coca | uithaler | witwas'],
    ["Toezicht & bevoegdheden",'cameratoezicht | preventief fouilleren | gebiedsverbod | noodverordening | bodycam'],
    ["Overlast & handhavers",'overlast | handhavers | boa | stadswacht'],
    ["Jaarwisseling & evenementen",'jaarwisseling | vuurwerk | rellen']]],
  ["Werk & inkomen",'bijstand | armoede | schulden | participatiewet | werkloos | bestaanszekerheid | minimabeleid',[
    ["Armoede & minima",'armoede | minimabeleid | rotterdampas | voedselbank | bestaanszekerheid'],
    ["Schulden",'schulden | schuldhulp | kredietbank | incasso'],
    ["Bijstand & participatie",'bijstand | participatiewet | tegenprestatie | uitkering'],
    ["Werk & re-integratie",'werkloos | re-integratie | basisbaan | arbeidsmarkt']]],
  ["Zorg, welzijn & jeugd",'jeugdzorg | wmo | welzijn | mantelzorg | ouderen | "ggd" | eenzaamheid | huisarts',[
    ["Jeugd & jeugdzorg",'jeugdzorg | jeugdhulp | wijkteam | veilig thuis'],
    ["Wmo & ondersteuning",'wmo | huishoudelijke hulp | mantelzorg | dagbesteding'],
    ["Ouderen",'ouderen | eenzaamheid | seniorenwoning'],
    ["Welzijn in de wijk",'welzijn | huis van de wijk | buurthuis'],
    ["Gezondheid",'"ggd" | huisarts | gezondheid | preventie | corona']]],
  ["Onderwijs",'onderwijs | school | scholen | leerling | leraren | kinderopvang',[
    ["Lerarentekort",'lerarentekort | leraren | leerkracht'],
    ["Kansengelijkheid",'kansengelijk | onderwijsachterstand | segregatie | schooladvies'],
    ["Schoolgebouwen",'schoolgebouw | onderwijshuisvesting'],
    ["Mbo & stages",'"mbo" | stage | beroepsonderwijs'],
    ["Voorschool & kinderopvang",'kinderopvang | voorschool | peuter']]],
  ["Economie & haven",'haven | ondernemer | economie | horeca | werkgelegenheid | winkel | "mkb"',[
    ["Haven & industrie",'havenbedrijf | haven | industrie | maasvlakte'],
    ["Ondernemers & mkb",'ondernemer | "mkb" | winkel | winkelstraat'],
    ["Horeca & nachtleven",'horeca | terras | nachtleven | nachtcultuur'],
    ["Toerisme",'toeris | hotel | cruiseschip | airbnb | vakantieverhuur'],
    ["Luchthaven",'rotterdam the hague airport | luchthaven | vliegveld']]],
  ["Cultuur, sport & evenementen",'cultuur | museum | "sport" | sportverenig | sportpark | evenement | festival | bibliothe',[
    ["Cultuurplan & instellingen",'cultuurplan | museum | theater | boijmans | bibliothe'],
    ["Sport",'"sport" | sportverenig | sportpark | zwembad | feyenoord'],
    ["Evenementen & festivals",'evenement | festival | songfestival | marathon']]],
  ["Financiën & belastingen",'begroting | jaarstukken | "ozb" | belasting | bezuinig | voorjaarsnota | weerstandsvermogen',[
    ["Begroting & jaarstukken",'begroting | jaarstukken | voorjaarsnota | 10-maands'],
    ["Lokale lasten",'"ozb" | afvalstoffenheffing | rioolheffing | woonlasten'],
    ["Bezuinigen & reserves",'bezuinig | weerstandsvermogen | reserves | ombuiging'],
    ["Deelnemingen",'eneco | stedin | deelneming | warmtebedrijf']]],
  ["Asiel & migratie",'asiel | statushouder | vluchteling | opvanglocatie | spreidingswet | arbeidsmigrant | "coa"',[
    ["Opvang & spreiding",'opvanglocatie | spreidingswet | "coa" | asielzoeker | silja'],
    ["Statushouders & inburgering",'statushouder | inburgering | taakstelling'],
    ["Oekraïne",'oekra'],
    ["Arbeidsmigranten",'arbeidsmigrant | uitzendbureau']]],
  ["Dienstverlening & organisatie",'dienstverlening | 14010 | stadswinkel | ambtenar | inhuur | reorganisatie | bedrijfsvoering',[
    ["Loketten & bereikbaarheid",'14010 | stadswinkel | dienstverlening | balie'],
    ["Inhuur & personeel",'inhuur | ambtenar | ziekteverzuim | reorganisatie'],
    ["Klachten & ombudsman",'ombudsman | klachten | bezwaar']]]]],
 ["Thema’s dwars door de organisatie",[
  ["AI & algoritmen",'"ai" | kunstmatige intelligentie | artificial intelligence | algoritme | chatgpt | generatieve | machine learning | taalmodel',[
    ["AI",'"ai" | kunstmatige intelligentie | artificial intelligence | chatgpt | generatieve | taalmodel'],
    ["Algoritmen & risicomodellen",'algoritme | risicomodel | profilering | algoritmeregister']]],
  ["Data & privacy",'privacy | "avg" | persoonsgegevens | datalek | gegevensbescherming | datagedreven | open data | dataset',[
    ["Privacy & AVG",'privacy | "avg" | persoonsgegevens | gegevensbescherming | datalek'],
    ["Datagedreven werken",'datagedreven | open data | dataset | dashboard']]],
  ["Digitalisering & ICT",'digitalis | digitale | "ict" | cyber | software | glasvezel | smart city',[
    ["Digitale inclusie",'digitale inclusie | digitaal vaardig | digibeet | laaggeletterd'],
    ["ICT & cyberveiligheid",'"ict" | cyber | hack | software'],
    ["Digitale stad",'smart city | digitale stad | glasvezel | sensor']]],
  ["Participatie & inspraak",'participatie | inspraak | wijkraad | wijkraden | referendum | burgerberaad | bewonersinitiatief',[
    ["Wijkraden & gebieden",'wijkraad | wijkraden | gebiedscommissie | wijkakkoord'],
    ["Referendum & burgerberaad",'referendum | burgerberaad | burgerpanel'],
    ["Inspraak & initiatieven",'inspraak | bewonersinitiatief | right to challenge']]],
  ["Discriminatie & inclusie",'discriminatie | racisme | inclusie | diversiteit | emancipatie | lhbt | toegankelijkheid',[]],
  ["Integriteit & transparantie",'integriteit | geheimhouding | "woo" | transparant | klokkenluider | belangenverstrengeling',[]],
  ["Inkoop, aanbesteding & subsidie",'aanbested | inkoop | subsidie | leverancier | contractmanagement',[]],
  ["Onderzoek & verantwoording",'rekenkamer | evaluatie | monitor | ombudsman | "audit" | accountant',[]],
  ["Innovatie & experimenten",'innovatie | "pilot" | experiment | proeftuin | start-up',[]],
  ["Regio & Rijk",'metropoolregio | "mrdh" | provincie | rijksoverheid | "vng" | kabinet',[]],
  ["Toezeggingen",'zeg ik toe | zeg ik u toe | toezegging | kan ik toezeggen | zeggen wij toe',[]]]],
 ["Wijken en gebieden",[
  ["Centrum",'stadsdriehoek | oude westen | scheepvaartkwartier | dijkzigt | coolsingel | lijnbaan | binnenweg | binnenrotte | "cool"',[
    ["Stadsdriehoek & Coolsingel",'stadsdriehoek | coolsingel | lijnbaan | binnenrotte | hoogstraat'],
    ["Oude Westen & Dijkzigt",'oude westen | dijkzigt | binnenweg | kruiskade'],
    ["Cool & Scheepvaartkwartier",'"cool" | scheepvaartkwartier | witte de with']]],
  ["Delfshaven",'delfshaven | spangen | bospolder | tussendijken | middelland | nieuwe westen | schiemond | mathenesse',[
    ["Bospolder-Tussendijken & Spangen",'bospolder | tussendijken | spangen | "botu"'],
    ["Middelland & Nieuwe Westen",'middelland | nieuwe westen'],
    ["Delfshaven-Schiemond",'historisch delfshaven | schiemond | lloydkwartier'],
    ["Mathenesse",'mathenesse | witte dorp']]],
  ["Noord",'oude noorden | agniesebuurt | provenierswijk | bergpolder | blijdorp | liskwartier',[
    ["Oude Noorden",'oude noorden'],
    ["Agniesebuurt-Provenierswijk",'agniesebuurt | provenierswijk'],
    ["Blijdorp-Bergpolder-Liskwartier",'blijdorp | bergpolder | liskwartier']]],
  ["Kralingen-Crooswijk",'kralingen | crooswijk | rubroek | "de esch" | struisenburg',[
    ["Kralingen",'kralingen | "de esch" | struisenburg'],
    ["Crooswijk",'crooswijk | rubroek']]],
  ["Feijenoord",'afrikaanderwijk | bloemhof | hillesluis | katendrecht | noordereiland | vreewijk | kop van zuid | wilhelminapier | parkstad | tweebosbuurt',[
    ["Afrikaanderwijk & Tweebosbuurt",'afrikaanderwijk | tweebosbuurt | parkstad'],
    ["Bloemhof & Hillesluis",'bloemhof | hillesluis | beijerlandselaan'],
    ["Katendrecht & Kop van Zuid",'katendrecht | wilhelminapier | kop van zuid | entrepot'],
    ["Vreewijk",'vreewijk'],
    ["Noordereiland",'noordereiland']]],
  ["IJsselmonde",'ijsselmonde | lombardijen | beverwaard | keizerswaard',[
    ["Groot- en Oud-IJsselmonde",'groot-ijsselmonde | oud-ijsselmonde | keizerswaard'],
    ["Lombardijen",'lombardijen'],
    ["Beverwaard",'beverwaard']]],
  ["Charlois",'charlois | tarwewijk | carnisse | pendrecht | zuidwijk | heijplaat | zuidplein | wielewaal',[
    ["Tarwewijk",'tarwewijk'],
    ["Carnisse & Zuidplein",'carnisse | zuidplein | zuiderpark'],
    ["Pendrecht & Zuidwijk",'pendrecht | zuidwijk'],
    ["Oud-Charlois & Wielewaal",'oud-charlois | oud charlois | wielewaal'],
    ["Heijplaat",'heijplaat']]],
  ["Hillegersberg-Schiebroek",'hillegersberg | schiebroek | terbregge | molenlaankwartier',[
    ["Hillegersberg",'hillegersberg | terbregge | molenlaankwartier'],
    ["Schiebroek",'schiebroek']]],
  ["Overschie",'overschie | zestienhoven',[]],
  ["Prins Alexander",'prins alexander | ommoord | zevenkamp | nesselande | oosterflank | het lage land | prinsenland | kralingseveer',[
    ["Ommoord",'ommoord'],
    ["Zevenkamp & Nesselande",'zevenkamp | nesselande'],
    ["Oosterflank, Lage Land & Prinsenland",'oosterflank | het lage land | prinsenland'],
    ["Kralingseveer",'kralingseveer']]],
  ["Hoogvliet",'hoogvliet',[]],
  ["Pernis",'pernis',[]],
  ["Rozenburg",'rozenburg',[]],
  ["Hoek van Holland",'hoek van holland',[]],
  ["Nationaal Programma Rotterdam Zuid",'"nprz" | nationaal programma rotterdam zuid | rotterdam-zuid | "op zuid"',[]]]]]
