# Invoerpakket voor een AI-samenvatting van één gebied (14 gebieden), zelfde opbouw als dossier_in.py.
#   python src/gebied_in.py <gebied-slug>   -> WERK/dossier/in_<slug>.md en bronnen_<slug>.json
# Bronnen: debatten en stukken die de wijk- of gebiedsnamen noemen (zelfde zoekpatronen als de gebiedskoppeling, fase 2).
# Daarna: opdracht src/gebied_prompt.md (Opus), controle met src/dossier_check.py <slug> --schrijf.
import json,os,re,sys
import gebieden as GB, dossier_in as DI
from paden import WERK
def main(g):
    WW=json.load(open(os.path.join(WERK,'wijk','wijken.json'),encoding='utf8'))
    H=json.load(open(os.path.join(WERK,'gebied','gebieden.json'),encoding='utf8'))['gebieden']
    gid=next(r['id'] for r in H if r['niveau']=='gebied' and DI.slug(r['naam'])==g)
    naam=next(r['naam'] for r in H if r['id']==gid)
    pats=[rx.pattern for s,rx in GB.wijkregex(WW) if s==gid or s in WW[gid]]
    DI.pakket(naam,re.compile('|'.join(f'(?:{p})' for p in pats)),'het gebied')
if __name__=='__main__': main(sys.argv[1])
