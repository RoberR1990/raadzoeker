# Volledige tekst van de rekenkamerrapporten (pdf) bij extern.py -> WERK/extern/rekenkamer_tekst.json
# Per onderzoek het bestuurlijk rapport en de nota van bevindingen (als die er zijn). Max 1 verzoek per seconde.
import json,os,re
import ibabs
from paden import WERK
def tekst(b):
    import pymupdf
    with pymupdf.open(stream=b,filetype='pdf') as d: return '\n'.join(p.get_text() for p in d)
if __name__=='__main__':
    R=json.load(open(os.path.join(WERK,'extern','rekenkamer.json'),encoding='utf8')); out={}
    for r in R:
        docs=[]
        for u in r['pdf']:
            naam=os.path.basename(u)
            if re.search(r'onderzoeksopzet|persbericht|praatplaat',naam,re.I): continue
            try:
                b=ibabs.get(u,binary=True)
                if b[:4]==b'%PDF': docs.append({'url':u,'naam':naam,'tekst':tekst(b)[:200000]})
            except Exception as e: print('fout',u,e)
        out[r['url']]=docs; print(r['titel'][:50],len(docs),sum(len(d['tekst']) for d in docs)//1000,'k tekens',flush=True)
    json.dump(out,open(os.path.join(WERK,'extern','rekenkamer_tekst.json'),'w',encoding='utf8'),ensure_ascii=False)
