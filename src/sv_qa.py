# Schriftelijke vragen van raadsleden mét het antwoord van het college (iBabs) -> WERK/ibabs/sv_qa.jsonl
# Per vraag: detailpagina, tekst van de vragen (pdf), en via 'Relatie met' de collegebrief met de beantwoording (pdf).
# Hervatbaar; gedeelde iBabs-limiet (max 1 verzoek per seconde); --minuten N om in blokken te draaien.
import json,os,re,sys,time
import ibabs,ibabs_items as I
from paden import WERK
OUT=os.path.join(WERK,'ibabs','sv_qa.jsonl')
def pdf(hd):
    if isinstance(hd,list) and hd:
        try: return (I.pdftekst(hd[0]['url']) or '')[:30000]
        except ibabs.Blokkade: raise
        except Exception: return ''
    return ''
if __name__=='__main__':
    args=sys.argv[1:]; stop=None
    if '--minuten' in args: stop=time.time()+60*float(args[args.index('--minuten')+1])
    L=json.load(open(os.path.join(WERK,'ibabs','lijsten.json'),encoding='utf8'))['schriftelijke_vragen']
    klaar=set()
    if os.path.exists(OUT):
        for l in open(OUT,encoding='utf8'):
            try: klaar.add(json.loads(l)['id'])
            except Exception: pass
    alleen=args[args.index('--alleen')+1] if '--alleen' in args else None   # gericht ophalen op titel
    todo=[r for r in L if (I.jaar(r) or 0)>=2018 and r['DT_RowId'] not in klaar and (not alleen or re.search(alleen,(r.get('title') or '').lower()))]
    todo.sort(key=lambda r:r['registrationdate'][6:10]+r['registrationdate'][3:5]+r['registrationdate'][:2],reverse=True)   # nieuwste eerst
    print('te doen',len(todo),'klaar',len(klaar),flush=True)
    try:
        with open(OUT,'a',encoding='utf8') as f:
            for k,r in enumerate(todo):
                d=I.parse(ibabs.get('/Reports/Item/'+r['DT_RowId']))
                x={'id':r['DT_RowId'],'lijst':r,'detail':d,'vraag':pdf(d.get('Hoofddocument'))}
                rel=[o for o in (d.get('Relatie met') or []) if isinstance(o,dict) and o.get('naam','').startswith('Brieven B&W')]
                if rel:
                    a=I.parse(ibabs.get('/Reports/Item/'+rel[0]['id']))
                    x['antwoord_id']=rel[0]['id']; x['antwoord_titel']=a.get('Titel',''); x['antwoord_datum']=a.get('Datum ontvangen') or a.get('Datum publicatie','')
                    x['antwoord']=pdf(a.get('Hoofddocument'))
                f.write(json.dumps(x,ensure_ascii=False)+'\n'); f.flush()
                if k%100==0: print(k,'/',len(todo),flush=True)
                if stop and time.time()>stop: print('tijd op, later verder',flush=True); break
    except ibabs.Blokkade as e:
        print('BLOKKADE, gestopt:',e); sys.exit(2)
