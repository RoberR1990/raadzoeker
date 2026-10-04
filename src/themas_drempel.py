# Fase 1c: drempelanalyse kandidaat-thema's die dwars door de domeinen lopen (alleen analyse).
#   python src/themas_drempel.py  -> WERK/labels/themas_drempel.txt
# Hoofdonderwerp = zoekterm in de titel, óf (bij stukken met tekst) minstens 3x in de tekst én al in de eerste 150 woorden.
# Losse vermeldingen tellen niet mee.
import json,os,re,collections
import domeinen as D, teksten as T
from paden import WERK

K=[
 ('AI en algoritmes',[r'kunstmatige intelligentie',r'\bai\b',r'algoritm',r'chatgpt',r'generatieve']),
 ('Data en privacy',[r'privacy',r'\bavg\b',r'persoonsgegevens',r'datalek',r'\bdata\b']),
 ('Digitalisering en ICT',[r'digitalis',r'\bict\b',r'digitale (overheid|dienstverlening|inclusie)']),
 ('Informatiebeveiliging en cyber',[r'informatiebeveilig',r'cyber',r'hack',r'ransomware']),
 ('Organisatieontwikkeling',[r'organisatieontwikkel',r'reorganisatie',r'concernorganisatie',r'werkgeverschap',r'ambtelijke organisatie']),
 ('Personeel en inhuur',[r'inhuur',r'personeelsbeleid',r'formatie',r'ambtenaren',r'medewerkers van de gemeente',r'ziekteverzuim']),
 ('Inkoop en aanbesteding',[r'aanbested',r'inkoop',r'social return']),
 ('Subsidies',[r'subsidie']),
 ('Participatie en inspraak',[r'participatie',r'inspraak',r'burgerberaad',r'right to challenge',r'buurtbudget']),
 ('Dienstverlening en klantcontact',[r'dienstverlening',r'klantcontact',r'14 ?010',r'wijkhub',r'stadswinkel']),
 ('Communicatie en voorlichting',[r'communicatie',r'voorlichting',r'campagne']),
 ('Integriteit',[r'integriteit',r'nevenfunctie',r'belangenverstrengeling']),
 ('Openbaarheid en transparantie',[r'\bwoo\b',r'\bwob\b',r'openbaarheid',r'transparant',r'actieve informatieplicht',r'geheimhouding']),
 ('Discriminatie en racisme',[r'discriminatie',r'racisme',r'antisemitisme',r'moslimhaat']),
 ('Toegankelijkheid en beperking',[r'toegankelijk',r'beperking',r'gehandicapt',r'vn.verdrag handicap',r'rolstoel']),
 ('Lhbtiq+ en gender',[r'lhbt',r'regenboog',r'gender',r'emancipatie']),
 ('Jongeren',[r'jongeren',r'jeugdbeleid',r'jongerenwerk']),
 ('Ouderen',[r'ouderen',r'senioren',r'vergrijzing']),
 ('Kansengelijkheid',[r'kansengelijkheid',r'kansenongelijkheid',r'gelijke kansen']),
 ('Laaggeletterdheid',[r'laaggeletterd',r'geletterdheid',r'taalachterstand']),
 ('Gezondheidsverschillen en preventie',[r'gezondheidsverschil',r'preventie',r'overgewicht',r'gezonde leefstijl']),
 ('Eenzaamheid',[r'eenzaam']),
 ('Mentale gezondheid',[r'mentale gezondheid',r'psychisch',r'ggz',r'verward']),
 ('Arbeidsmigranten',[r'arbeidsmigrant']),
 ('Asiel en statushouders',[r'asiel',r'statushouder',r'vluchteling',r'\bazc\b',r'oekraïn',r'oekrain']),
 ('Polarisatie en radicalisering',[r'polarisatie',r'radicalis',r'extremis',r'desinformatie']),
 ('Slavernijverleden',[r'slavernij',r'keti koti']),
 ('Circulaire economie',[r'circulair',r'grondstoffen',r'hergebruik']),
 ('Klimaatadaptatie en hitte',[r'klimaatadaptatie',r'hittestress',r'wateroverlast',r'weerwoord']),
 ('Energiearmoede',[r'energiearmoede',r'energiearm',r'energierekening',r'energietoeslag']),
 ('Biodiversiteit en groen',[r'biodiversiteit',r'vergroen',r'stadsnatuur']),
 ('Regio en Rijk',[r'\bmrdh\b',r'metropoolregio',r'het rijk\b',r'rijksoverheid',r'regio deal',r'g4\b',r'provincie']),
 ('Europa en internationaal',[r'europe',r'\beu\b',r'stedenband',r'internationa']),
 ('Innovatie en experimenten',[r'innovatie',r'experiment',r'pilot',r'proeftuin']),
 ('Onderzoek en evaluatie',[r'evaluatie',r'rekenkamer',r'onderzoeksrapport',r'monitor']),
 ('Nachteconomie',[r'nachtcultuur',r'nachtleven',r'nachtburgemeester',r'nachtplan',r'24.uurs']),
 ('Erfgoed en monumenten',[r'erfgoed',r'monument']),
 ('Wijkgericht werken en wijkraden',[r'wijkraad',r'wijkgericht',r'wijkakkoord',r'wijkaanpak',r'gebiedscommissie']),
 ('Vrijwilligers en maatschappelijk initiatief',[r'vrijwillig',r'bewonersinitiatie',r'maatschappelijk initiatief',r'sociale initiatieven']),
 ('Grote evenementen en gaststad',[r'songfestival',r'tour de france',r'gaststad',r'grote evenementen',r'wk\b',r'\bek\b']),
]
RX=[(n,re.compile(r'\b(?:'+'|'.join(pp)+r')',re.I)) for n,pp in K]

def main():
    m,tekst=D.tekstdocs()
    ap=D.agendapunten()
    lab=json.load(open(os.path.join(WERK,'labels','domein.json'),encoding='utf8'))
    tel=collections.defaultdict(set); tel22=collections.defaultdict(set); dom=collections.defaultdict(collections.Counter)
    def doe(k,datum,titel,tx):
        ft=T.fold(titel); fx=T.fold(tx) if tx else ''
        kop=' '.join(fx.split()[:150])
        for n,r in RX:
            if r.search(ft) or (fx and len(r.findall(fx))>=3 and r.search(kop)):
                tel[n].add(k)
                if datum>='2022': tel22[n].add(k)
                d=lab.get(k,[None])[0]
                if d: dom[n][d]+=1
    for i,r in enumerate(m['d']):
        if m['soorten'][r[0]] in ('Wijkraadvergadering',): continue
        doe(f't:{i}',r[1],r[2],tekst(i))
    for a in ap: doe(a[0],a[2],a[4],'')
    out=['Kandidaat-thema\'s: aantal stukken/agendapunten waarin het thema hoofdonderwerp is',
         f'{"thema":45} {"2018-2026":>9} {"2022-2026":>9}  domeinen (top 3)']
    for n,_ in sorted(K,key=lambda x:-len(tel[x[0]])):
        out.append(f'{n:45} {len(tel[n]):9} {len(tel22[n]):9}  '+', '.join(f'{D.NAAM[d]} {v*100//max(1,sum(dom[n].values()))}%' for d,v in dom[n].most_common(3)))
    out.append('\nAantal thema\'s boven de drempel (2018-2026 / 2022-2026), en wat afvalt:')
    for t in (5,10,15,20,50,100):
        af=[n for n,_ in K if len(tel[n])<t]; af22=[n for n,_ in K if len(tel22[n])<t]
        out.append(f'  >= {t:3}: {len(K)-len(af):2} / {len(K)-len(af22):2}   valt af (2022+): {", ".join(af22) or "-"}')
    open(os.path.join(WERK,'labels','themas_drempel.txt'),'w',encoding='utf8').write('\n'.join(out))
    print('\n'.join(out))

if __name__=='__main__': main()
