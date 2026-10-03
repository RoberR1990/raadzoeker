# Bijlagen als tekst (iBabs), hervatbaar, gedeelde iBabs-limiet:
#   python src/bijlagen.py rv  [--minuten N]   raadsvoorstellen: pdf van het hoofddocument -> WERK/ibabs/rv_tekst.jsonl
#   python src/bijlagen.py wrb [--minuten N]   bijlagen bij wijkraadvergaderingen -> WERK/wijk/wijkraad_bijlagen.jsonl
# Collegebrieven: python src/ibabs_items.py brieven (hoofddocument als tekst).
import json,os,re,sys,time,html
import ibabs,ibabs_items as I
from paden import WERK
W='https://wijkraad.rotterdam.nl'
def klaar(p,veld='id'):
    s=set()
    if os.path.exists(p):
        for l in open(p,encoding='utf8'):
            try: s.add(json.loads(l)[veld])
            except Exception: pass
    return s
def rv(stop):
    p=os.path.join(WERK,'ibabs','rv_tekst.jsonl'); k=klaar(p)
    items=[json.loads(l) for l in open(os.path.join(WERK,'ibabs','items_raadsvoorstellen.jsonl'),encoding='utf8')]
    todo=[x for x in items if x['id'] not in k]; print('raadsvoorstellen te doen',len(todo),flush=True)
    with open(p,'a',encoding='utf8') as f:
        for x in todo:
            hd=x['detail'].get('Hoofddocument') or x['detail'].get('Document'); t=''
            if isinstance(hd,list) and hd:
                try: t=(I.pdftekst(hd[0]['url']) or '')[:60000]
                except ibabs.Blokkade: raise
                except Exception: t=''
            f.write(json.dumps({'id':x['id'],'tekst':t},ensure_ascii=False)+'\n'); f.flush()
            if stop and time.time()>stop: return False
    return True
def wrb(stop):
    p=os.path.join(WERK,'wijk','wijkraad_bijlagen.jsonl'); k=klaar(p,'doc')
    V=[json.loads(l) for l in open(os.path.join(WERK,'wijk','wijkraadvergaderingen.jsonl'),encoding='utf8')]
    docs=[]
    for v in V:
        h=ibabs.get(W+'/Agenda/Index/'+v['id'])   # uit de cache: geen nieuw verzoek
        for did,naam in re.findall(r'href="/Agenda/Document/[0-9a-f-]+\?documentId=([0-9a-f-]+)[^"]*"[^>]*>(.*?)</a>',h,re.S):
            n=re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',naam))).strip()
            docs.append((v['id'],did,n))
    docs=list(dict.fromkeys(docs)); todo=[d for d in docs if d[1] not in k]
    print('wijkraad-bijlagen',len(docs),'te doen',len(todo),flush=True)
    with open(p,'a',encoding='utf8') as f:
        for aid,did,naam in todo:
            t=''
            try:
                b=ibabs.get(W+'/Document/View/'+did,binary=True)
                if b[:4]==b'%PDF':
                    import pymupdf
                    with pymupdf.open(stream=b,filetype='pdf') as d: t='\n'.join(pg.get_text() for pg in d)[:60000]
            except ibabs.Blokkade: raise
            except Exception: t=''
            f.write(json.dumps({'verg':aid,'doc':did,'naam':naam,'tekst':t},ensure_ascii=False)+'\n'); f.flush()
            if stop and time.time()>stop: return False
    return True
if __name__=='__main__':
    a=sys.argv[1:]; stop=time.time()+60*float(a[a.index('--minuten')+1]) if '--minuten' in a else None
    try:
        klaar_=globals()[a[0]](stop)
        print('klaar' if klaar_ else 'tijd op, later verder',flush=True)
    except ibabs.Blokkade as e:
        print('BLOKKADE, gestopt:',e); sys.exit(2)
