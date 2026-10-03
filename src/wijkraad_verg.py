# Vergaderingen van de wijkraden (wijkraad.rotterdam.nl, iBabs) 2022-nu -> WERK/wijk/wijkraadvergaderingen.jsonl
# Per vergadering: wijkraad, datum, agendapunten met toelichting en besluit (staan als tekst op de pagina).
# Hervatbaar; gedeelde iBabs-limiet (ibabs.py, max 1 verzoek per seconde); stopt bij een blokkade.
import json,os,re,sys,html,datetime
import ibabs
from paden import WERK
W='https://wijkraad.rotterdam.nl'
OUT=os.path.join(WERK,'wijk','wijkraadvergaderingen.jsonl')
def tekst(s): return re.sub(r'[ \t]+',' ',html.unescape(re.sub(r'<br\s*/?>|</p>|</li>','\n',re.sub(r'<script.*?</script>','',s,flags=re.S)))).strip()
def schoon(s): return re.sub(r'\n\s*\n+','\n',re.sub(r'<[^>]+>',' ',s)).strip()
MND={m:i+1 for i,m in enumerate('januari februari maart april mei juni juli augustus september oktober november december'.split())}
def lees(h):
    b=h[h.find('Vorige pagina'):]
    kop=re.search(r'Vorige pagina</a>\s*(.*?)(?=<div class="[^"]*agenda-item|Agendapunten)',b,re.S)
    k=re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',kop.group(1) if kop else ''))).strip()
    m=re.search(r'(\w+dag)? ?(\d{1,2}) (\w+) (\d{4})',k); datum=f'{m.group(4)}-{MND.get(m.group(3).lower(),0):02d}-{int(m.group(2)):02d}' if m and m.group(3).lower() in MND else ''
    items=[]
    for blok in re.split(r'<div class="panel panel-default agenda-item"',h)[1:]:
        nr=re.search(r'class="panel-id"[^>]*>(.*?)<',blok,re.S); ti=re.search(r'class="panel-title-label"[^>]*>(.*?)</',blok,re.S)
        body=re.search(r'class="panel-body"[^>]*>(.*)',blok,re.S)
        items.append({'nr':schoon(nr.group(1)) if nr else '','titel':schoon(html.unescape(ti.group(1))) if ti else '',
                      'tekst':re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',body.group(1)[:20000] if body else ''))).strip()[:2000]})
    return k,datum,items
if __name__=='__main__':
    klaar=set()
    if os.path.exists(OUT):
        for l in open(OUT,encoding='utf8'):
            try: klaar.add(json.loads(l)['id'])
            except Exception: pass
    verg={}
    try:
        for j in range(2022,datetime.date.today().year+1):
            for m in range(0,12):   # maanden tellen vanaf 0
                h=ibabs.get(W+f'/Calendar/GetMonthAgendas?month={m}&year={j}')
                for aid,tid,lab in re.findall(r'href="/Agenda/Index/([0-9a-f-]+)"[^>]*data-agendatype-id="(\d+)"[^>]*>\s*<div class="calendar-item-label">\s*([^<]+)',h):
                    verg[aid]=(tid,re.sub(r'\s+',' ',html.unescape(lab)).strip())
        print(len(verg),'vergaderingen,',len(klaar),'al gedaan',flush=True)
        with open(OUT,'a',encoding='utf8') as f:
            for k,(aid,(tid,lab)) in enumerate(sorted(verg.items())):
                if aid in klaar: continue
                kop,datum,items=lees(ibabs.get(W+'/Agenda/Index/'+aid))
                f.write(json.dumps({'id':aid,'type':tid,'raad':lab,'datum':datum,'kop':kop[:300],'items':items},ensure_ascii=False)+'\n'); f.flush()
                if k%200==0: print(k,'/',len(verg),flush=True)
    except ibabs.Blokkade as e:
        print('BLOKKADE, gestopt:',e); sys.exit(2)
    print('klaar')
