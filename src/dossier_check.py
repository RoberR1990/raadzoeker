# Mechanische controle van een onderwerpsamenvatting (WERK/dossier/uit_<slug>.json) tegen bronnen_<slug>.json.
# Een zin/punt blijft alleen staan als het citaat woordelijk in de genoemde bron staat; bij fracties moet de bron
# van die fractie zijn (debat: partij van de spreker; motie/vragen: indiener); bij het college een college-bron.
# Status van moties/toezeggingen komt uit iBabs (veld 'stand'), niet van het model.
#   python src/dossier_check.py <slug> [--schrijf]   -> met --schrijf: WERK/dossier/ok_<slug>.json en docs/ontwerp/samenvattingen/
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
    if code[0] in 'TSV': return True
    if code[0]=='D': return bool(re.search(r'wethouder|burgemeester|college',(b.get('rol','')+' '+b.get('wie','')).lower())) and not b.get('partij')
    return False
def main(slug,schrijf):
    B=json.load(open(os.path.join(WERK,'dossier',f'bronnen_{slug}.json'),encoding='utf8'))['bronnen']
    U=json.load(open(os.path.join(WERK,'dossier',f'uit_{slug}.json'),encoding='utf8'))
    NB={c:norm(b['tekst']) for c,b in B.items()}
    tel={}; weg=[]
    def toets(x,deel,eis=None):
        c=(x.get('bron') or '').strip('[] '); b=B.get(c); cit=norm(x.get('citaat',''))
        red=None
        if not b: red='bron bestaat niet'
        elif len(cit.split())<4: red='citaat te kort'
        elif cit not in NB[c]: red='citaat staat niet in de bron'
        elif eis and eis.startswith('fractie:') and not fractie_ok(eis[8:],b,c): red='bron is niet van deze fractie'
        elif eis=='college' and not college_ok(b,c): red='geen bron van het college'
        elif eis=='college' and c[0]=='V' and cit not in norm(b['tekst'].partition('ANTWOORD VAN HET COLLEGE')[2]): red='citaat niet uit het antwoord'
        a,n=tel.get(deel,(0,0)); tel[deel]=(a+(red is None),n+1)
        if red: weg.append((deel,red,c,x.get('citaat','')[:90])); return None
        x=dict(x); x['url']=b['url']; x['bron_datum']=b['datum']
        if c[0]=='D':   # kort: 'Naam (partij), commissie Mobiliteit'
            v=re.sub(r'\s*\(\d{4}\s*-\s*\d{4}\)','',b.get('verg','')); v=re.sub(r'^Commissie (\w+).*',r'commissie \1',v)
            x['bron_label']=b.get('wie','')+(' ('+b['partij']+')' if b.get('partij') else '')+', '+v
        else: x['bron_label']=b.get('soort','')+' ‘'+re.sub(r'^(Afdoeningsvoorstel|Raadsvoorstel over|Afschrift brief)\s*','',b.get('titel',''))[:70].strip()+'’'
        if c[0]=='D': x['auto']=b.get('auto',False)
        if c[0] in 'TM' and b.get('status'): x['stand']=b['status']
        return x
    lijst=lambda xs,deel,eis=None:[y for y in (toets(x,deel,eis) for x in xs or []) if y]
    ok={'onderwerp':U.get('onderwerp',slug)}
    ok['kern']=lijst(U.get('kern'),'kern')
    ok['verdieping']=[a for a in (lijst(p,'verdieping') for p in U.get('verdieping') or []) if a]
    for deel,eis in(('tijdlijn',None),('fracties',None),('college','college'),('wijken',None),('open',None)):
        d=U.get(deel) or {}
        o={'intro':lijst(d.get('intro'),deel+'.intro','college' if deel=='college' else None)}
        if deel=='fracties':
            o['punten']=[{'fractie':f['fractie'],'standpunten':s} for f in d.get('punten') or [] if (s:=lijst(f.get('standpunten'),'fracties','fractie:'+f.get('fractie','')))]
        else: o['punten']=lijst(d.get('punten'),deel,eis)
        if deel=='tijdlijn': o['punten'].sort(key=lambda x:x['bron_datum'],reverse=True)   # nieuw naar oud
        ok[deel]=o
    for w in weg: print(' weg',*w)
    print(slug,{k:f'{a}/{n}' for k,(a,n) in tel.items()})
    if schrijf:
        from paden import DOCS
        from onderwerpen import O
        ok['telling']={k:f'{a} van {n}' for k,(a,n) in tel.items()}
        ok['zoek']=next((p[0].replace('\\b','') for n,p in O if n==ok['onderwerp']),'')
        json.dump(ok,open(os.path.join(WERK,'dossier',f'ok_{slug}.json'),'w',encoding='utf8'),ensure_ascii=False,indent=1)
        d=os.path.join(DOCS,'ontwerp','samenvattingen'); os.makedirs(d,exist_ok=True)
        json.dump(ok,open(os.path.join(d,f'{slug}.json'),'w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
        pi=os.path.join(d,'index.json'); idx=json.load(open(pi,encoding='utf8')) if os.path.exists(pi) else []
        idx=[x for x in idx if x['slug']!=slug]+[{'slug':slug,'naam':ok['onderwerp']}]
        json.dump(idx,open(pi,'w',encoding='utf8'),ensure_ascii=False)
if __name__=='__main__': main(sys.argv[1],'--schrijf' in sys.argv)
