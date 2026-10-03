# Geregistreerde misdrijven per buurt per jaar (politie, via CBS-tabel 47018NED, open data) -> WERK/wijk/politie.json
# Alleen Rotterdamse buurten (BU0599...), 2018-2025, een selectie herkenbare soorten. Max 1 verzoek per seconde.
import json,os,time,urllib.request,urllib.parse
from paden import WERK
B='https://dataderden.cbs.nl/ODataApi/OData/47018NED/TypedDataSet'
SOORT={'0.0.0':'Totaal misdrijven','1.1.1':'Woninginbraak','1.2.3':'Fietsdiefstal','1.4.4':'Bedreiging','1.4.5':'Mishandeling','1.4.6':'Straatroof',
       '1.6.1':'Brand of ontploffing','2.1.1':'Drugs- en drankoverlast','2.2.1':'Vernieling','3.1.1':'Drugshandel'}
def haal(code):
    # ca. 92 buurten x 8 jaar per soort, ruim onder de grens van 10.000 rijen per verzoek
    f=f"startswith(WijkenEnBuurten,'BU0599') and SoortMisdrijf eq '{code.ljust(6)}' and Perioden ge '2018JJ00'"
    url=B+'?'+urllib.parse.urlencode({'$filter':f,'$format':'json'})
    with urllib.request.urlopen(url,timeout=120) as r: v=json.load(r)['value']
    time.sleep(1.05); assert len(v)<10000
    return v
if __name__=='__main__':
    out={}
    for code,naam in SOORT.items():
        rows=haal(code)
        for r in rows:
            out.setdefault(r['WijkenEnBuurten'].strip(),{}).setdefault(naam,{})[r['Perioden'][:4]]=r['GeregistreerdeMisdrijven_1']
        print(naam,len(rows),flush=True)
    json.dump({'bron':'Politie, geregistreerde misdrijven per buurt (CBS 47018NED)','soorten':list(SOORT.values()),'buurten':out},
              open(os.path.join(WERK,'wijk','politie.json'),'w',encoding='utf8'),ensure_ascii=False)
    print(len(out),'buurten')
