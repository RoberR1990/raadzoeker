# Wijkprofiel Rotterdam (OBI, gemeente Rotterdam): sociale, fysieke en veiligheidsindex per gebied en wijk,
# edities 2014-2026, van de openbare pagina's -> WERK/wijk/wijkprofiel.json
# Bronvermelding (verplicht): Cijfers: gemeente Rotterdam; OBI, Wijkprofiel 2014-2026.
# Max 1 verzoek per seconde (ibabs.get), met cache. Index 100 = gemiddelde van Rotterdam in 2014.
import json,os,re,html,sys
import ibabs
from paden import WERK
B='https://wijkprofiel.rotterdam.nl/'
JAREN=['2014','2016','2018','2020','2022','2024','2026']
def tekst(s): return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',s))).strip()
def lees(h):
    out={}
    for cls,tb in re.findall(r'<table class="(\w\w)_tabel">(.*?)</table>',h,re.S):
        cap=tekst(re.search(r'<caption>(.*?)</caption>',tb,re.S).group(1)); m=re.search(r'(-?\d+)\s*$',cap)
        d={'index':int(m.group(1)) if m else None}
        rows=re.findall(r'<tr[^>]*>(.*?)</tr>',tb,re.S); kol=[]
        for row in rows:
            cel=[tekst(c) for c in re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>',row,re.S)]
            if not cel: continue
            if 'hoofdrij' in row or cel[0].startswith('Algemeen'):
                v=[c for c in cel[1:] if re.fullmatch(r'-?\d+',c)]
                d['algemeen']=[cel[0].replace('Algemeen','').strip(),int(v[0]) if v else None]
            elif cel[0]=='' and len(cel)>1: kol=cel[1:]
            elif cel[0] in('Subjectief','Objectief'):
                vals=[c for c in cel[1:]]
                d[cel[0].lower()]={k:(int(v) if re.fullmatch(r'-?\d+',v) else None) for k,v in zip(kol,vals)}
        out={'fi':'fysiek','vi':'veiligheid','si':'sociaal'}[cls] and out
        out[{'fi':'fysiek','vi':'veiligheid','si':'sociaal'}[cls]]=d
    return out
def main():
    os.makedirs(os.path.join(WERK,'wijk'),exist_ok=True)
    r=ibabs.get(B+'nl/2026/rotterdam')
    gebieden=sorted(set(re.findall(r'href="(?:'+re.escape(B)+r')?nl/2026/rotterdam/([a-z-]+)"',r)))
    paden=[('rotterdam','')]
    for g in gebieden:
        h=ibabs.get(B+f'nl/2026/rotterdam/{g}')
        paden.append((g,g))
        for w in sorted(set(re.findall(r'href="(?:'+re.escape(B)+r')?nl/2026/rotterdam/'+g+r'/([a-z-]+)"',h))):
            if w!=g: paden.append((g,g+'/'+w))
    print(len(paden),'pagina\'s per editie',flush=True)
    data={}
    for j in JAREN:
        for g,p in paden:
            url=B+f'nl/{j}/rotterdam'+('/'+p if p else '')
            try: h=ibabs.get(url)
            except Exception as e: continue
            w=lees(h)
            if not w: continue
            naam=tekst((re.search(r'<title>(.*?)</title>',h,re.S) or [None,''])[1]) if False else p
            data.setdefault(p or 'rotterdam',{})[j]=w
        print(j,'klaar',flush=True)
    json.dump({'bron':'Cijfers: gemeente Rotterdam; OBI, Wijkprofiel 2014-2026','paden':paden,'data':data},
              open(os.path.join(WERK,'wijk','wijkprofiel.json'),'w',encoding='utf8'),ensure_ascii=False)
    print('wijkprofiel',len(data),'gebieden/wijken')
if __name__=='__main__': main()
