# Steekproefhulp voor themasamenvattingen: welke namen/getallen uit de samenvatting staan niet in het invoerbestand?
# Gebruik: python src/tsum_check.py 08 10 ...   (vergelijkt data/tsum/out_NN.json met WERK/tsum/in_NN.txt)
# Gewone werkwoorden aan het zinsbegin komen ook in de lijst; let op eigennamen (straten, wijken, personen).
import json,re,sys
from paden import DATA,WERK
for nn in sys.argv[1:]:
    blocks=re.split(r'(?=### THEMA id=)',open(f'{WERK}/tsum/in_{nn}.txt',encoding='utf8').read())
    for d in json.load(open(f'{DATA}/tsum/out_{nn}.json',encoding='utf8')):
        b=[x for x in blocks if x.startswith(f'### THEMA id={d["id"]} ')][0].lower()
        toks=set(re.findall(r'\b[A-Z][a-zà-ÿ]{3,}(?:[- ][A-Z][a-zà-ÿ]+)*|\b\d{2,}\b',json.dumps(d,ensure_ascii=False)))
        print(d['id'],'niet in bron:',sorted(t for t in toks if t.lower() not in b and not re.match(r'^(19|20)\d\d$',t)))
