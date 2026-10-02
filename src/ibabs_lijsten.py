# Haalt de metadata-lijsten van alle iBabs-rapportages op -> WERK/ibabs/lijsten.json
import json,os,collections
import ibabs
from paden import WERK
R={'toezeggingen':'32881df4-b70b-4ede-942c-d4135415883f','moties':'a61fab39-bc62-464f-968d-db31925a66e5','amendementen':'f7307a5e-0e03-4360-a88a-c0b56202c747',
   'raadsvoorstellen':'4a6cb9e4-2668-4729-852a-ddb3b3ea90d3','initiatiefvoorstellen':'f477a1ec-3ab8-472f-9d4f-a1cb60fa3b88','besluiten':'ed13ec46-0027-4992-b3ac-eaa1d8dcbdab',
   'brieven':'a164b9e0-5669-4508-8669-fc94780c5131','schriftelijke_vragen':'da9b533f-5f24-4f51-8567-19fe410f15d4','wijkraadadviezen':'85c7d75a-22d0-497e-ae8e-8d993f41ed32'}
if __name__=='__main__':
    out={}
    for n,rid in R.items():
        rows,_=ibabs.report_all(rid); out[n]=rows
        jr=collections.Counter((r.get('registrationdate') or r.get('datumbesluit') or '????')[-4:] for r in rows)
        print(n,len(rows),sorted(jr.items())[-12:],flush=True)
    json.dump(out,open(os.path.join(WERK,'ibabs','lijsten.json'),'w',encoding='utf8'),ensure_ascii=False)
