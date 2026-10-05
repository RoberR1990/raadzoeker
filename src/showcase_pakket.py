# Bronpakket voor de AI-samenvatting van een voorbeelddossier (showcase.CONFIG), met de relevante pagina's van het coalitieakkoord als bron S900.
#   python src/showcase_pakket.py <slug>   -> WERK/dossier/in_<slug>.md en bronnen_<slug>.json
# Daarna: opdracht src/dossier_prompt.md (Opus), controle met src/dossier_check.py <slug> --schrijf, dan src/dossier_data.py.
import re,sys
import akkoord,dossier_in as DI,showcase
from ontwerp_data import fold
def main(slug):
    c=showcase.CONFIG[slug]; P=akkoord.paginas()
    dicht=sorted(((len(re.findall(c['rx'],fold(p))),i) for i,p in enumerate(P,1)),reverse=True)
    pg=sorted(i for n,i in dicht[:12] if n>=2)
    tekst=' […] '.join(f'(blz. {i}) '+re.sub(r'\s+',' ',P[i-1]) for i in pg)
    extra={'S900':{'soort':'Coalitieakkoord','datum':'2026-07-15','titel':akkoord.TITEL+f" (PRO, D66, VVD, CDA, Volt), pagina's over {c['naam'].lower()}",
                   'wie':'Coalitie PRO, D66, VVD, CDA en Volt','url':akkoord.URL,'tekst':tekst}}
    DI.pakket(c['naam'],re.compile(c['rx']),'het domein' if c.get('label') else 'het onderwerp',extra=extra); print('akkoord blz.',pg)
if __name__=='__main__':
    for s in sys.argv[1:]: main(s)
