import json,re,os,html
from bs4 import BeautifulSoup
RAW='/home/claude/raw'
h=json.load(open(f'{RAW}/header.json'))
MND={m:i+1 for i,m in enumerate('januari februari maart april mei juni juli augustus september oktober november december'.split())}
out=[]
for m in h['meetings']:
    s=open(f"{RAW}/agenda/{m['year']}/{m['id']}.html",encoding='utf8').read()
    s=re.sub(r'src="data:[^"]*"','src=""',s)
    i=s.find('id="agendaitems"')
    soup=BeautifulSoup(s[i-200:] if i>0 else s,'lxml')
    mm=re.match(r'\w+ (\d+) (\w+) (\d{4})\s*(.*)',m['label'])
    date='%s-%02d-%02d'%(mm.group(3),MND[mm.group(2)],int(mm.group(1)))
    vid=re.search(r'data-video-id="([^"]*)"',s)
    tm=re.search(r'<dt[^>]*>\s*Tijd\s*</dt>\s*<dd[^>]*>\s*([^<]*)',s)
    items=[]
    for it in soup.select('div.agenda-item'):
        nr=it.select_one('.panel-id'); tl=it.select_one('.panel-title-label')
        sp=[]
        for o in it.select('div.speakers > div.offset'):
            t=' '.join(o.get_text().split())
            sp.append((t,o.get('data-off')))
        items.append({'id':it.get('id'),'nr':nr.get_text(strip=True) if nr else '','title':' '.join(tl.get_text().split()) if tl else '','sp':sp})
    out.append({'id':m['id'],'date':date,'label':m['label'],'suffix':mm.group(4),'video':vid.group(1) if vid else None,'time':tm.group(1).strip() if tm else None,'items':items})
json.dump(out,open('agendas.json','w'),ensure_ascii=False)
import collections
print(len(out), sum(len(a['items']) for a in out), sum(len(i['sp']) for a in out for i in a['items']))
print(collections.Counter(a['date'][:4] for a in out if any(i['sp'] for i in a['items'])))
print(collections.Counter(a['suffix'] for a in out).most_common(30))
ex=[i['sp'] for a in out for i in a['items'] if i['sp']]
import random; random.seed(1)
for e in random.sample(ex,6): print(e[:3])
print([ (a['date'],a['label'],len(a['items']),a['video'],a['time']) for a in out[-28:]])
