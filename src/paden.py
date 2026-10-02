# Alle paden op één plek. Overschrijfbaar met omgevingsvariabelen.
import os
SRC=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.dirname(SRC)
DATA=os.path.join(ROOT,'data')
DOCS=os.path.join(ROOT,'docs')
# grote bronbestanden (niet in git)
BRON=os.environ.get('RZ_BRON',r'D:\Downloads Chrome')
BUNDLE=os.path.join(BRON,'raadzoeker-bundle (1).dat')
# werkmap voor tussenbestanden (raw/, lines/, agendas.json, segs.json, out/, outc/; ca. 1 GB), naast de bronbestanden
WERK=os.environ.get('RZ_WERK',os.path.join(BRON,'raadzoeker-werk'))
RAW=os.path.join(WERK,'raw')
# stand van de data (datum van ophalen); bepaalt ook welke toekomstige vergaderingen worden overgeslagen
STAND=os.environ.get('RZ_STAND','2026-10-02')
