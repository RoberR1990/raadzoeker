# Mechanische controle van een onderwerpsamenvatting (WERK/dossier/uit_<slug>.json) tegen bronnen_<slug>.json.
# Een bewering blijft alleen staan als het citaat woordelijk in de genoemde bron staat; bij fracties moet de bron
# van die fractie zijn (debat: partij van de spreker; motie/vragen: indiener); bij het college een college-bron.
#   python src/dossier_check.py <slug> [--schrijf]   -> met --schrijf: WERK/dossier/ok_<slug>.json (alleen goedgekeurd)
import json,os,re,sys,unicodedata
from paden import WERK
def norm(s):
    s=''.join(c for c in unicodedata.normalize('NFD',s.lower()) if unicodedata.category(c)!='Mn')
    s=re.sub(r'[‘’‚`´]',"'",s); s=re.sub(r'[“”„]','"',s); s=s.replace('…','...').replace('-\n','')
    return re.sub(r'[^a-z0-9]+',' ',s).strip()
def fractie_ok(f,b,code):
    f=norm(f)
    if code[0]=='D': return bool(b.get('partij')) and (norm(b['partij'])==f or f in norm(b['partij']) or norm(b['partij']) in f)
    if code[0] in 'MV': return norm(b.get('wie','')).startswith(f) or f in norm(b.get('wie','')[:60])
    return False
def college_ok(b,code):
    if code[0] in 'TS': return True
    if code[0]=='V': return True   # citaat moet dan in het antwoord staan (zie onder)
    if code[0]=='D': return bool(re.search(r'wethouder|burgemeester|college',(b.get('rol','')+' '+b.get('wie','')).lower())) and not b.get('partij')
    return False
def main(slug,schrijf):
    B=json.load(open(os.path.join(WERK,'dossier',f'bronnen_{slug}.json'),encoding='utf8'))['bronnen']
    U=json.load(open(os.path.join(WERK,'dossier',f'uit_{slug}.json'),encoding='utf8'))
    NB={c:norm(b['tekst']) for c,b in B.items()}
    ok={k:v for k,v in U.items() if not isinstance(v,list)}; tel={}
    for deel in('kern','tijdlijn','fracties','college','wijken','open'):
        goed=[]; fout=[]
        for x in U.get(deel,[]):
            c=(x.get('bron') or '').strip('[] '); b=B.get(c); cit=norm(x.get('citaat',''))
            red=None
            if not b: red='bron bestaat niet'
            elif len(cit.split())<4: red='citaat te kort'
            elif cit not in NB[c]: red='citaat staat niet in de bron'
            elif deel=='fracties' and not fractie_ok(x.get('fractie',''),b,c): red='bron is niet van deze fractie'
            elif deel=='college' and not college_ok(b,c): red='geen bron van het college'
            elif deel=='college' and c[0]=='V' and cit not in norm(b['tekst'].partition('ANTWOORD VAN HET COLLEGE')[2]): red='citaat niet uit het antwoord'
            if red: fout.append((red,c,x.get('citaat','')[:90]))
            else:
                x=dict(x); x['url']=b['url']; x['bron_datum']=b['datum']
                x['bron_label']=(b.get('verg','')+' · '+b.get('wie','')) if c[0]=='D' else b.get('soort','')+' · '+b.get('titel','')[:120]
                if c[0]=='D': x['auto']=b.get('auto',False)
                if c[0] in 'TM' and b.get('status'): x['stand']=b['status']   # status uit iBabs, niet van het model
                goed.append(x)
        ok[deel]=goed; tel[deel]=(len(goed),len(U.get(deel,[])))
        for f in fout: print(' weg',deel,f)
    print(slug,{k:f'{a}/{b}' for k,(a,b) in tel.items()})
    if schrijf:
        # ook publiceren naar de proefpagina docs/ontwerp/samenvatting.html
        from paden import DOCS
        from onderwerpen import O
        ok['telling']={k:f'{a} van {b}' for k,(a,b) in tel.items()}
        ok['zoek']=next((p[0].replace('\\b','') for n,p in O if n==ok.get('onderwerp')),'')
        json.dump(ok,open(os.path.join(WERK,'dossier',f'ok_{slug}.json'),'w',encoding='utf8'),ensure_ascii=False,indent=1)
        d=os.path.join(DOCS,'ontwerp','samenvattingen'); os.makedirs(d,exist_ok=True)
        json.dump(ok,open(os.path.join(d,f'{slug}.json'),'w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
        pi=os.path.join(d,'index.json'); idx=json.load(open(pi,encoding='utf8')) if os.path.exists(pi) else []
        idx=[x for x in idx if x['slug']!=slug]+[{'slug':slug,'naam':ok.get('onderwerp',slug)}]
        json.dump(idx,open(pi,'w',encoding='utf8'),ensure_ascii=False)
if __name__=='__main__': main(sys.argv[1],'--schrijf' in sys.argv)
