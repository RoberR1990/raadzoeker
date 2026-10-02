# Stap 6: wijkraden (wijkraad.rotterdam.nl, ook iBabs) -> WERK/ibabs/wijk.jsonl
# Ongevraagde adviezen, wijkakkoorden en -plannen, reacties van het college op wijkplannen, wijkverslagen:
# lijst + detailpagina + tekst van het hoofddocument. Hervatbaar; gedeelde iBabs-limiet (ibabs.py).
# De gevraagde wijkraadadviezen staan in de raads-iBabs (ibabs_items.py wijkraadadviezen).
import json,os,sys
import ibabs,ibabs_items as I
from paden import WERK
W='https://wijkraad.rotterdam.nl'
R={'ongevraagd':'8e253588-02c5-4190-88fe-ed34f24f7fe5','wijkakkoorden':'3f05f73b-a90b-47ee-9841-dcd534803cde',
   'reacties':'858a546a-bd3a-4a17-a8bc-605038ad4ea7','verslagen':'8d760582-7bc3-4152-a43e-fd3d9eae7198'}
if __name__=='__main__':
    out=os.path.join(WERK,'ibabs','wijk.jsonl'); klaar=set()
    if os.path.exists(out):
        for l in open(out,encoding='utf8'):
            try: klaar.add(json.loads(l)['id'])
            except Exception: pass
    try:
        with open(out,'a',encoding='utf8') as f:
            for naam,rid in R.items():
                rows,_=ibabs.report_all(rid,base=W); print(naam,len(rows),flush=True)
                for r in rows:
                    if r['DT_RowId'] in klaar: continue
                    d={'id':r['DT_RowId'],'soort':naam,'lijst':r,'detail':I.parse(ibabs.get(W+'/Reports/Item/'+r['DT_RowId']))}
                    hd=d['detail'].get('Hoofddocument') or d['detail'].get('Document')
                    if isinstance(hd,list) and hd:
                        try: d['tekst']=I.pdftekst(hd[0]['url'],W)
                        except ibabs.Blokkade: raise
                        except Exception as e: d['tekstfout']=str(e)[:200]
                    f.write(json.dumps(d,ensure_ascii=False)+'\n'); f.flush()
    except ibabs.Blokkade as e:
        print('BLOKKADE, gestopt:',e); sys.exit(2)
    print('klaar')
