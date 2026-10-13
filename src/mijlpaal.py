# Grote updates voor 'Wat is er nieuw' -> docs/data/mijlpalen.json (pagina docs/nieuw.html, blok 'Grote updates').
# Los van logboek.json: dat bestand schrijft alleen de NAS-run; dit bestand alleen routines en handwerk, zodat ze nooit botsen.
#   python src/mijlpaal.py nieuw "titel" "tekst" [--soort functie|samenvattingen|data] [--link "tekst|url"]...
#   python src/mijlpaal.py verg <id8> ...   (roept verg_batch.py check zelf aan: nieuwe vergadersamenvattingen;
#                                            op dezelfde dag samengevoegd tot één regel)
import json,os,sys,datetime
from paden import DOCS

LOG=os.path.join(DOCS,'data','mijlpalen.json')

def lees():
    try: return json.load(open(LOG,encoding='utf8'))
    except (OSError,ValueError): return {'regels':[]}

def schrijf(L):
    L['regels'].sort(key=lambda r:r['datum'],reverse=True)
    json.dump(L,open(LOG,'w',encoding='utf8'),ensure_ascii=False,indent=0)

def vandaag(): return datetime.date.today().isoformat()

def nieuw(titel,tekst,soort='functie',links=()):
    L=lees(); L['regels'].append({'datum':vandaag(),'soort':soort,'titel':titel,'tekst':tekst,'links':[{'t':t,'u':u} for t,u in links]}); schrijf(L)

def verg(ids):
    I={v['id']:v for v in json.load(open(os.path.join(DOCS,'verg','index.json'),encoding='utf8'))}
    nw=[{'t':f"{I[k]['naam']} · {I[k]['datum']}",'u':f"vergadering.html?id={k}",'d':I[k]['datum']} for k in ids if k in I]
    if not nw: return
    L=lees(); d=vandaag()
    r=next((r for r in L['regels'] if r['datum']==d and r['soort']=='samenvattingen' and r.get('auto')),None)
    if r is None: r={'datum':d,'soort':'samenvattingen','auto':1,'links':[]}; L['regels'].append(r)
    al={x['u'] for x in r['links']}; r['links']+=[x for x in nw if x['u'] not in al]
    r['links'].sort(key=lambda x:x['d'],reverse=True); n=len(r['links'])
    r['titel']=f"{n} {'vergadering' if n==1 else 'vergaderingen'} samengevat"
    r['tekst']='Nieuwe AI-samenvattingen op de vergaderpagina: korte versie, per agendapunt wat er gezegd is, met letterlijke citaten die automatisch gecontroleerd zijn.'
    schrijf(L); print(f'mijlpaal: {len(nw)} vergaderingen bij {d}')

if __name__=='__main__':
    a=sys.argv[1:]
    if a[:1]==['verg']: verg(a[1:])
    elif a[:1]==['nieuw'] and len(a)>=3:
        soort='functie'; links=[]; rest=a[3:]
        while rest:
            k,v,rest=rest[0],rest[1],rest[2:]
            if k=='--soort': soort=v
            elif k=='--link': links.append(tuple(v.split('|',1)))
        nieuw(a[1],a[2],soort,links)
    else: sys.exit(__doc__ or 'gebruik: mijlpaal.py nieuw "titel" "tekst" [--soort s] [--link "tekst|url"] | verg <id8>...')
