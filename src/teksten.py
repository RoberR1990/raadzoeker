# Volledige teksten van stukken samen doorzoekbaar -> docs/data/tekst/
#   meta.zst      {soorten, d:[[soort, datum, titel, wie, url, lengte(woorden)], ...], stand}
#   i/NNN.zst     zoekindex, NI shards op hash van de stam: {stam:[[docid-delta,...],[tf,...]]}
#   b/NNN.zst     teksten per blok van BLOK documenten: [tekst, ...]
# Bronnen (werkmap): raadsvoorstellen (rv_tekst), rekenkamerrapporten (pdf), schriftelijke vragen + antwoord (sv_qa),
# collegebrieven (items_brieven), wijkraadvergaderingen + bijlagen, en de overige stukken met tekst uit stukken.zst.
# Document-id's blijven gelijk tussen builds (WERK/teksten/ids.json), zodat ongewijzigde blokken byte-gelijk blijven.
import json,os,re,glob,unicodedata,collections,zstandard
from paden import WERK,DOCS,STAND
OUT=os.path.join(DOCS,'data','tekst'); NI=512; BLOK=64; MAXT=150000
W='https://wijkraad.rotterdam.nl'; G='https://gemeenteraad.rotterdam.nl'
def fold(s): return ''.join(c for c in unicodedata.normalize('NFD',s.lower()) if unicodedata.category(c)!='Mn')
def stam(w):
    # zelfde regels als in zoek.html
    if len(w)>5 and w.endswith('en'): w=w[:-2]
    elif len(w)>4 and w.endswith('s') and not w.endswith('ss'): w=w[:-1]
    if len(w)>4 and w.endswith('e'): w=w[:-1]
    return w
def woorden(t): return [stam(w) for w in re.findall(r'[a-z0-9]+',fold(t)) if 2<=len(w)<=30]
def h(s):   # FNV-1a 32 bit, ook in zoek.html
    x=0x811c9dc5
    for c in s.encode('utf8'): x=((x^c)*0x01000193)&0xffffffff
    return x%NI
def iso(d):
    m=re.match(r'\s*(\d\d)-(\d\d)-(\d{4})',d or '')
    return f'{m.group(3)}-{m.group(2)}-{m.group(1)}' if m else (d or '')[:10]
def schoon(t): return re.sub(r'\n\s*\n+','\n',re.sub(r'[ \t\xa0]+',' ',(t or '').replace('\r',''))).strip()[:MAXT]
# Privacy (besloten 3-10-2026): in wijkraadteksten namen van insprekers/bewoners weglakken. Binnen een venster na
# 'inspreek…'/'spreekt in' en na aanspreekvormen worden reeksen met hoofdletters (met voorletters/tussenvoegsels) '[naam]'.
# Straat- en plaatsnamen blijven staan. Vangt niet alles; liever iets te veel dan te weinig weg.
TV=r'(?:van|de|der|den|het|ter|ten|te|op|in|\'t|la|le|el|al|bin|ben)'
NAAM=re.compile(r'\b(?!(?:Bewoners?|Insprekers?|Inspreekrecht|Inspreektijd|Wijkraad|Wethouder|Voorzitter|Besluit|De|Het|Een|Er|Wel|Geen)\b)(?:(?:[A-Z]\.\s?){1,4}\s?|[A-Z][a-zà-ÿ]+(?:-[A-Z][a-zà-ÿ]+)?\s+)(?:'+TV+r'\s+){0,3}[A-Z][a-zà-ÿ]+(?:-[A-Z][a-zà-ÿ]+)?\b')
GEEN=re.compile(r'(straat|weg|plein|laan|kade|park|singel|dreef|wijk|buurt|raad|gemeente|rotterdam|college|centrum|school|kerk|wethouder|voorzitter|agenda|besluit|commissie)\b',re.I)
AANSPR=re.compile(r'(\b(?:[Dd]hr|[Mm]evr|[Mm]w|[Dd]e heer|[Mm]evrouw)\.?\s+)(?:(?:[A-Z]\.\s?){1,4}\s?)?(?:'+TV+r'\s+){0,3}[A-Z][a-zà-ÿ]+(?:[\s-]+[A-Z][a-zà-ÿ]+)?')
def anoniem(t):
    vervang=lambda s:NAAM.sub(lambda m:m.group(0) if GEEN.search(m.group(0)) else '[naam]',s)
    uit=[];i=0
    for m in re.finditer(r'[Ii]nspre[ek]k\w*|[Ii]nsprekers?|spreekt in|komt inspreken',t):
        if m.start()<i: continue
        e=min(len(t),m.end()+500); uit+=[t[i:m.start()],vervang(t[m.start():e])]; i=e
    t=''.join(uit)+t[i:]
    return AANSPR.sub(lambda m:m.group(1)+'[naam]',t)   # 'de heer X', 'mevr. Y' overal in wijkraadteksten
def jl(p):
    if os.path.exists(p):
        for l in open(p,encoding='utf8'):
            try: yield json.loads(l)
            except Exception: pass
def bronnen():
    I=os.path.join(WERK,'ibabs')
    # raadsvoorstellen: hoofddocument
    rv={d['id']:d['tekst'] for d in jl(os.path.join(I,'rv_tekst.jsonl'))}
    for d in jl(os.path.join(I,'items_raadsvoorstellen.jsonl')):
        r=d['lijst']; t=rv.get(d['id'],'') or d['detail'].get('Omschrijving','')
        if t: yield 'rv:'+d['id'],'Raadsvoorstel',iso(r.get('registrationdate')),r.get('title',''),r.get('portefeuillehouder',''),G+'/Reports/Item/'+d['id'],t
    # rekenkamer: alle pdf's van het onderzoek
    p=os.path.join(WERK,'extern','rekenkamer_tekst.json')
    if os.path.exists(p):
        T=json.load(open(p,encoding='utf8'))
        for x in json.load(open(os.path.join(WERK,'extern','rekenkamer.json'),encoding='utf8')):
            t='\n\n'.join(f['tekst'] for f in T.get(x['url'],[]) if f.get('tekst')) or x.get('tekst','')
            yield 'rk:'+x['url'],'Rekenkamerrapport',x['datum'],x['titel'],x.get('domein',''),x['url'],t
    # schriftelijke vragen met het antwoord van het college
    for d in jl(os.path.join(I,'sv_qa.jsonl')):
        r=d['lijst']; wie=(r.get('partij') or '')+(' ('+r['raadslid'].strip()+')' if r.get('raadslid') else '')
        t='VRAGEN\n'+(d.get('vraag') or '')
        if d.get('antwoord'): t+='\n\nANTWOORD VAN HET COLLEGE'+(' ('+d['antwoord_datum']+')' if d.get('antwoord_datum') else '')+'\n'+d['antwoord']
        yield 'sv:'+d['id'],'Schriftelijke vragen',iso(r.get('registrationdate')),r.get('title',''),wie,G+'/Reports/Item/'+d['id'],t
    # collegebrieven (ibabs_items.py brieven)
    for d in jl(os.path.join(I,'items_brieven.jsonl')):
        r=d['lijst']; t=d.get('tekst') or d.get('detail',{}).get('Omschrijving','')
        if t: yield 'cb:'+d['id'],'Collegebrief',iso(r.get('registrationdate')),r.get('title',''),r.get('portefeuillehouder',''),G+'/Reports/Item/'+d['id'],t
    # wijkraden: vergadering (agenda met toelichting en besluit) en de bijlagen
    V={v['id']:v for v in jl(os.path.join(WERK,'wijk','wijkraadvergaderingen.jsonl'))}
    for v in V.values():
        if not v['datum'] or v['datum']>STAND: continue
        t='\n'.join((i['nr']+' '+i['titel']+'\n'+i['tekst']).strip() for i in v['items'])
        if t: yield 'wv:'+v['id'],'Wijkraadvergadering',v['datum'],v['raad']+' '+v['datum'],v['raad'],W+'/Agenda/Index/'+v['id'],anoniem(t)
    for d in jl(os.path.join(WERK,'wijk','wijkraad_bijlagen.jsonl')):
        v=V.get(d['verg'])
        if not v or not d['tekst'].strip(): continue
        naam=re.sub(r'\s+\d+([.,]\d+)?\s*[KM]B$','',d['naam']).strip()
        yield 'wb:'+d['doc'],'Wijkraadstuk',v['datum'],naam,v['raad'],W+'/Document/View/'+d['doc'],anoniem(d['tekst'])
    # overige stukken met tekst (moties, toezeggingen, amendementen, wijkraadadviezen, ...), zonder dubbele soorten
    ST=json.loads(zstandard.ZstdDecompressor().decompress(open(os.path.join(DOCS,'data','ibabs','stukken.zst'),'rb').read(),max_output_size=10**9))
    S=ST['soorten']; al={'Raadsvoorstel','Rekenkamerrapport','Schriftelijke vragen','Collegebrief'}
    for r in ST['s']:
        if S[r[0]] in al or len(r[6])<80: continue
        url=r[7] if r[7].startswith('http') else G+'/Reports/Item/'+r[7]
        yield 'st:'+r[7],S[r[0]],r[1],r[2],r[3],url,r[6]
def main():
    os.makedirs(os.path.join(OUT,'i'),exist_ok=True); os.makedirs(os.path.join(OUT,'b'),exist_ok=True)
    pid=os.path.join(WERK,'teksten','ids.json'); os.makedirs(os.path.dirname(pid),exist_ok=True)
    ids=json.load(open(pid,encoding='utf8')) if os.path.exists(pid) else {}
    docs={}
    for key,soort,datum,titel,wie,url,t in bronnen():
        t=schoon(t)
        if key in docs or not t: continue
        if key not in ids: ids[key]=len(ids)
        docs[ids[key]]=(soort,datum,re.sub(r'\s+',' ',titel or '').strip(),re.sub(r'\s+',' ',wie or '').strip(),url,t)
    json.dump(ids,open(pid,'w',encoding='utf8'))
    N=len(ids); soorten=sorted({d[0] for d in docs.values()}); si={s:i for i,s in enumerate(soorten)}
    post=collections.defaultdict(list); meta=[]
    for i in range(N):
        d=docs.get(i)
        if not d: meta.append(None); continue
        ws=woorden(d[2]+' '+d[2]+' '+d[5])   # titel telt dubbel
        meta.append([si[d[0]],d[1],d[2][:300],d[3][:120],d[4],len(ws)])
        for w,c in collections.Counter(ws).items(): post[w].append((i,min(c,255)))
    n=len(docs); grens=n*0.4
    shards=[{} for _ in range(NI)]
    for w,p in post.items():
        if len(p)>grens: continue   # stopwoorden
        ds=[p[0][0]]+[p[k][0]-p[k-1][0] for k in range(1,len(p))]
        shards[h(w)][w]=[ds,[c for _,c in p]]
    zc=zstandard.ZstdCompressor(level=19); tot=0
    def schrijf(p,obj):
        nonlocal tot
        b=zc.compress(json.dumps(obj,ensure_ascii=False,separators=(',',':')).encode('utf8'))
        if not os.path.exists(p) or open(p,'rb').read()!=b: open(p,'wb').write(b)
        tot+=len(b)
    for k,sh in enumerate(shards): schrijf(os.path.join(OUT,'i',f'{k:03d}.zst'),sh)
    for b in range(0,N,BLOK): schrijf(os.path.join(OUT,'b',f'{b//BLOK:03d}.zst'),[docs[i][5] if i in docs else '' for i in range(b,min(N,b+BLOK))])
    schrijf(os.path.join(OUT,'meta.zst'),{'soorten':soorten,'d':meta,'stand':STAND,'ni':NI,'blok':BLOK})
    print(n,'documenten',len(post),'stammen',round(tot/1e6,1),'MB', dict(collections.Counter(d[0] for d in docs.values())))
if __name__=='__main__': main()
