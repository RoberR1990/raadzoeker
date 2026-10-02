# Stap 5: Rekenkamer Rotterdam en Ombudsman Rotterdam-Rijnmond (ORR) -> WERK/extern/{rekenkamer,ombudsman}.json
# Rustig ophalen via ibabs.get (max 1 verzoek/sec, cache). Alleen Rotterdam, vanaf 2017 (rapporten uit 2017 komen in 2018 in de raad).
import json,os,re,html
import ibabs
from paden import WERK
OUT=os.path.join(WERK,'extern'); os.makedirs(OUT,exist_ok=True)
def tekst(s): return re.sub(r'[ \t]+',' ',html.unescape(re.sub(r'<[^>]+>',' ',s))).strip()
def iso(d):
    m=re.search(r'(\d\d)-(\d\d)-(\d{4})',d or ''); return f'{m.group(3)}-{m.group(2)}-{m.group(1)}' if m else ''
def rekenkamer():
    B='https://rekenkamer.rotterdam.nl'
    h=ibabs.get(B+'/onderzoeken')
    it=re.findall(r'<div class="row-audit-item" data-gemeente="([^"]*)" data-jaar="([^"]*)" data-status="([^"]*)" data-domein="([^"]*)" data-url="([^"]*)">(.*?)(?=<div class="row-audit-item"|</section>)',h,re.S)
    out=[]
    for gem,jaar,status,dom,url,blok in it:
        if 'Rotterdam' not in gem or not jaar or int(jaar)<2017: continue
        titel=tekst(re.search(r'<h5>(.*?)</h5>',blok,re.S).group(1))
        d=ibabs.get(B+url); m=d[d.find('<main'):d.find('</main>')]
        datum=iso(tekst(m[:3000])) or f'{jaar}-01-01'
        body=tekst(m)
        body=re.sub(r'^.*?Terug naar overzicht\s*','',body,flags=re.S)
        body=body.split('Meer weten over dit onderzoek')[0].split('Tijdslijn')[0].strip()
        pdfs=re.findall(r'href="(/docs/onderzoeken/[^"]+\.pdf)"',m)
        out.append({'titel':titel,'datum':datum,'status':status,'domein':dom.replace('|',', '),'url':B+url,'tekst':body[:6000],'pdf':[B+p for p in pdfs]})
    json.dump(out,open(os.path.join(OUT,'rekenkamer.json'),'w',encoding='utf8'),ensure_ascii=False,indent=1)
    print('rekenkamer',len(out))
def ombudsman():
    out=[]
    for cat,soort in((71,'Rapport'),(65,'Jaarverslag'),(92,'Brief')):
        page=1
        while True:
            r=json.loads(ibabs.get(f'https://orr.nl/wp-json/wp/v2/posts?categories={cat}&per_page=100&page={page}&_fields=id,date,link,title,content'))
            for p in r:
                tx=tekst(p['content']['rendered'])
                if p['date'][:4]<'2017' or 'Rotterdam' not in tx+p['title']['rendered']: continue
                out.append({'titel':tekst(p['title']['rendered']),'datum':p['date'][:10],'soort':soort,'url':p['link'],'tekst':tx[:6000]})
            if len(r)<100: break
            page+=1
    json.dump(out,open(os.path.join(OUT,'ombudsman.json'),'w',encoding='utf8'),ensure_ascii=False,indent=1)
    print('ombudsman',len(out))
if __name__=='__main__':
    rekenkamer(); ombudsman()
