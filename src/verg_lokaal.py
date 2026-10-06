# Proef: dezelfde vergadersamenvatting met een lokaal model (Ollama), ter vergelijking met Claude.
#   python src/verg_lokaal.py <agendaId> <model>   -> WERK/verg/uit_<id8>_<model>.json, daarna verg_check met dat pad
# Grote vergaderingen worden per agendapunt samengevat (kleine modellen hebben een korte context) en daarna samengevoegd.
import json,os,re,sys,time,urllib.request
from paden import WERK,DATA
OLLAMA='http://localhost:11434/api/generate'
def vraag(model,prompt,ctx=16384):
    body=json.dumps({'model':model,'prompt':prompt,'stream':False,'format':'json','options':{'num_ctx':ctx,'temperature':0.2}}).encode()
    t=time.time()
    with urllib.request.urlopen(urllib.request.Request(OLLAMA,data=body,headers={'Content-Type':'application/json'}),timeout=3600) as r: d=json.load(r)
    return d['response'],time.time()-t,d.get('prompt_eval_count'),d.get('eval_count')
def main(ag,model):
    k=ag[:8]; tekst=open(os.path.join(WERK,'verg',f'in_{k}.txt'),encoding='utf8').read()
    opdracht=open(os.path.join(os.path.dirname(__file__),'verg_prompt.md'),encoding='utf8').read()
    opdracht=re.sub(r'Lees het hele invoerbestand.*?overslaat\.','Het invoerbestand staat hieronder.',opdracht,flags=re.S).replace('Schrijf daarna met de Write-tool het uitvoerbestand: geldige JSON','Geef als antwoord alleen geldige JSON')
    opdracht=opdracht.split('Antwoord na het schrijven')[0]
    kop,*delen=re.split(r'\n(?=## )',tekst)
    totaal=[0,0,0]; kort=[]; aps=[]
    groepen=[]; huidig=kop
    for dl in delen:
        if len((huidig+dl).split())>5000 and huidig!=kop: groepen.append(huidig); huidig=kop
        huidig+='\n'+dl
    groepen.append(huidig)
    for g in groepen:
        if '(procedureel' in g and len(g.split())<400: continue
        uit,sec,pin,pout=vraag(model,opdracht+'\n\n=== INVOERBESTAND ===\n'+g)
        totaal[0]+=sec; totaal[1]+=pin or 0; totaal[2]+=pout or 0
        try: d=json.loads(uit)
        except Exception: print('geen geldige JSON'); continue
        kort+=d.get('kort',[]); aps+=d.get('agendapunten',[])
        print(f'deel: {sec:.0f}s, in {pin} uit {pout} tokens')
    out={'kort':kort[:7],'agendapunten':aps,'model':model}
    p=os.path.join(WERK,'verg',f'uit_{k}_{model.replace(":","-")}.json'); json.dump(out,open(p,'w',encoding='utf8'),ensure_ascii=False,indent=1)
    print(p,f'totaal {totaal[0]:.0f}s, in {totaal[1]} uit {totaal[2]} tokens')
if __name__=='__main__': main(*sys.argv[1:3])
