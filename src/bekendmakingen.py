# Officiële bekendmakingen van de gemeente Rotterdam (Gemeenteblad, via de open SRU-API van repository.overheid.nl)
# -> WERK/wijk/bekendmakingen.jsonl (hervatbaar per maand; --recent haalt deze en vorige maand opnieuw op). Per stuk: datum, soort, titel, omschrijving, activiteit, locatiepunt, url.
# Max 1 verzoek per seconde.
import json,os,re,sys,time,html,urllib.request,urllib.parse,datetime
from paden import WERK
SRU='https://repository.overheid.nl/sru'
OUT=os.path.join(WERK,'wijk','bekendmakingen.jsonl'); KLAAR=os.path.join(WERK,'wijk','bekendmakingen.maanden')
def veld(rec,naam):
    m=re.search(r'<(?:\w+:)?'+naam+r'(?:\s[^>]*)?>(.*?)</(?:\w+:)?'+naam+'>',rec,re.S); return html.unescape(m.group(1)).strip() if m else ''
def maand(j,m):
    begin=datetime.date(j,m,1); eind=(begin+datetime.timedelta(days=32)).replace(day=1)
    q=f'(c.product-area==officielepublicaties)and(dt.creator=="Rotterdam")and(w.publicatienaam==Gemeenteblad)and(dt.date>={begin})and(dt.date<{eind})'
    start=1;uit=[]
    while True:
        url=SRU+'?'+urllib.parse.urlencode({'query':q,'maximumRecords':1000,'startRecord':start})
        for poging in range(3):
            try:
                with urllib.request.urlopen(url,timeout=180) as r: t=r.read().decode('utf8')
                break
            except Exception as e:
                time.sleep(10)
        else: raise RuntimeError('mislukt: '+url)
        time.sleep(1.05)
        recs=re.findall(r'<sru:record>(.*?)</sru:record>',t,re.S)
        for rec in recs:
            p=veld(rec,'locatiepunt').split()
            uit.append({'d':veld(rec,'date'),'type':veld(rec,'type'),'titel':veld(rec,'title'),'oms':veld(rec,'abstract')[:300],
                        'act':veld(rec,'activiteit'),'lat':float(p[0]) if len(p)==2 else None,'lon':float(p[1]) if len(p)==2 else None,'url':veld(rec,'preferredUrl')})
        n=int(re.search(r'numberOfRecords>(\d+)',t).group(1))
        start+=len(recs)
        if not recs or start>n: return uit
if __name__=='__main__':
    klaar=set(open(KLAAR).read().split()) if os.path.exists(KLAAR) else set()
    vandaag=datetime.date.today()
    if '--recent' in sys.argv:   # nachtelijke run: deze en vorige maand opnieuw ophalen (er komen elke dag bekendmakingen bij)
        vorige=(vandaag.replace(day=1)-datetime.timedelta(days=1)).strftime('%Y-%m'); opnieuw={vorige,vandaag.strftime('%Y-%m')}
        if os.path.exists(OUT):
            rij=[l for l in open(OUT,encoding='utf8') if l.strip() and json.loads(l).get('d','')[:7] not in opnieuw]
            tmp=OUT+'.tmp'; open(tmp,'w',encoding='utf8').writelines(rij); os.replace(tmp,OUT)
        klaar-=opnieuw; open(KLAAR,'w').write(chr(10).join(sorted(klaar))+chr(10))
    with open(OUT,'a',encoding='utf8') as f:
        for j in range(2018,vandaag.year+1):
            for m in range(1,13):
                k=f'{j}-{m:02d}'
                if k in klaar or datetime.date(j,m,1)>vandaag: continue
                rows=maand(j,m)
                for r in rows: f.write(json.dumps(r,ensure_ascii=False)+'\n')
                f.flush(); open(KLAAR,'a').write(k+'\n'); print(k,len(rows),flush=True)
    print('klaar')
