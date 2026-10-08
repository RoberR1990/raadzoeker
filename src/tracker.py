# Beloftemonitor en dossiertijdlijn, zonder AI en zonder werkmap: alles komt uit docs/ (RZ_WERK is niet nodig).
#   python src/tracker.py
# Leest:  docs/data/ibabs/stukken.zst (alle iBabs-stukken), docs/data/tekst/{meta,labels}.zst (domein en gebieden per document, via de itemId in de url),
#         docs/data/ibabs/moties.json + docs/data/raad/JAAR.zst (stemuitslag, raadsvergadering en agendapunt per motie/amendement),
#         docs/data/debat/{meta.zst,b/*.zst} (alle agendapunten van raad en commissies, sprekers en videoseconde),
#         docs/d/index.json (lijst van dossiers) en onderwerpen.py/themes.py (zoekpatronen per onderwerp/thema).
#   STAND = env RZ_STAND, anders de nieuwste datum in stukken.zst (niet paden.STAND, dat is een vaste standaardwaarde).
# Schrijft (alleen als de inhoud wijzigt, compact JSON):
#   docs/beloofd.json     alle OPEN moties en toezeggingen (status 4)
#   docs/beloofd-af.json  afgedaan (status 5) met afdoeningsdatum in de laatste 24 maanden voor STAND
#     {"stand","dom":[[slug,naam]],"geb":[naam],"ond":[[slug,naam]],"kol":[...],"r":[rij,...]}  (r: nieuwste datum eerst)
#     kol = soort (0 motie/1 toezegging), datum, titel, wie, commissie, dom (index of -1), geb (bitmasker op "geb"), status, verwacht, afgedaan, bb, id (itemId;
#     iBabs: https://gemeenteraad.rotterdam.nl/Reports/Item/<id>), tekst, stappen [[datum,type,label,itemId|'']], stem [aangenomen,voor,tegen,zijde,fracties]|null,
#     ond (indexen in "ond"), ph (portefeuillehouder, alleen moties, uit de gekoppelde afdoeningsvoorstel-/tussenberichtbrief)
#   docs/lijn/<slug>.json  per dossier uit d/index.json een tijdlijn van gebeurtenissen (onderwerp/thema vanaf 2018, domein/gebied/kruising vanaf 2022, max 1.500)
#     {"stand","naam","soort","sinds","tel":{...},"e":[[datum,type,kant,titel,sub,url,x],...],("afgekapt":true)}  (e: nieuwste eerst)
#   docs/lijn/index.json  {slug: aantal gebeurtenissen}
# Een stuk hoort bij een onderwerp/thema als het patroon in de gevouwen titel staat of >= 3x in de eerste 6000 tekens tekst (zelfde regel als ontwerp_data.py);
# een debat (agendapunt) als het patroon in de gevouwen titel staat of >= 3x in alle tekst van dat agendapunt; bij domein/gebied/kruising via de labels.
import json,os,re,sys,glob,datetime,collections,unicodedata,zstandard
from paden import DOCS
import themes,onderwerpen
from ontwerp_data import rx as rx_thema,iso,kort,motiekern

OUT=DOCS; LIJN=os.path.join(OUT,'lijn')
dz=zstandard.ZstdDecompressor()
def zload(p): return json.loads(dz.decompress(open(p,'rb').read(),max_output_size=10**10))
def jload(p): return json.load(open(p,encoding='utf8'))
_MN={i:None for i in range(sys.maxunicode+1) if unicodedata.category(chr(i))=='Mn'}
def fold(s):   # gelijk aan fold() in ontwerp_data.py (kleine letters, NFD, accenten (Mn) weg, kromme aanhalingstekens recht), maar snel
    s=s.lower()
    if not s.isascii(): s=unicodedata.normalize('NFD',s).translate(_MN).replace('’',"'").replace('‘',"'")
    return s
def slug(s):   # gelijk aan slug() in dossier_data.py en ontwerp.js
    s=''.join(c for c in unicodedata.normalize('NFD',s.lower()) if unicodedata.category(c)!='Mn').replace('&',' ')
    return re.sub(r'[^a-z0-9]+','-',s).strip('-')
def schrijf(p,obj):
    b=json.dumps(obj,ensure_ascii=False,separators=(',',':')).encode('utf8')
    try:
        if open(p,'rb').read()==b: return False
    except OSError: pass
    open(p,'wb').write(b); return True
MND=['jan','feb','mrt','apr','mei','jun','jul','aug','sep','okt','nov','dec']
def dk(d): return f'{int(d[8:])} {MND[int(d[5:7])-1]} {d[:4]}'
def zonder_wh(s): return re.sub(r'\s*\(Wethouder\)','',s or '').strip()
def rl(r): return 'https://gemeenteraad.rotterdam.nl/Reports/Item/'+r[7] if not r[7].startswith('http') else r[7]

# ---------- 'Stand van zaken' uit de stuktekst (docs-only variant van stappen() in showcase.py) ----------
DAT=re.compile(r'(\d{1,2})-(\d{1,2})-(\d{4})')
BBX=re.compile(r'\d{2}bb\d+',re.I)
def svz(tekst):
    """[(datum ISO, soort, label, bb|None)] uit het blok 'Stand van zaken:' (tot de eerste lege regel of regel zonder datum)."""
    if 'Stand van zaken' not in (tekst or ''): return []
    blok=tekst.split('Stand van zaken',1)[1].lstrip(': \t')
    regels=[]
    for i,l in enumerate(blok.split('\n')):
        if not l.strip(): break
        if i and not DAT.search(l): break
        regels.append(l)
    out=[]
    for l in regels:
        ms=list(DAT.finditer(l)); pos=0
        for k,m in enumerate(ms):
            pre=l[pos:m.start()]; nxt=ms[k+1].start() if k+1<len(ms) else len(l)
            after=l[m.end():nxt]; bb=None
            pm=re.match(r'\s*\(([^)]*)\)',after)
            if pm: x=BBX.search(pm.group(1)); bb=x.group(0).lower() if x else None; pos=m.end()+pm.end()
            else:
                x=BBX.search(after); bb=x.group(0).lower() if x else None; pos=m.end()
            lab=re.sub(r'[\s:;,]+$','',re.sub(r'^[\s:;,]+','',pre))
            if not lab and not pm: lab=re.sub(r'[\s:;,]+$','',re.sub(r'^[\s:;,]+','',BBX.sub('',after)))
            try: dt=datetime.date(int(m.group(3)),int(m.group(2)),int(m.group(1))).isoformat()
            except ValueError: continue
            low=lab.lower()
            soort='tussenbericht' if ('tussen' in low or 'voortgang' in low) else 'afdoeningsvoorstel' if 'afdoening' in low else 'commissieadvies' if 'commissie' in low else 'overig'
            tekstlab={'tussenbericht':'Tussenbericht van het college','afdoeningsvoorstel':'Afdoeningsvoorstel van het college','commissieadvies':'Advies van de commissie'}.get(soort,lab or 'Overig')
            out.append((dt,soort,tekstlab,bb))
    return out
VOLG={'ingediend':0,'toegezegd':0,'stemming':1,'tussenbericht':2,'afdoeningsvoorstel':3,'commissieadvies':3,'overig':3,'verwacht':4,'afgedaan':5}

PROC=re.compile(r'^(?:opening|sluiting|mededelingen?|rondvraag|ingekomen stukken?|hamerstukken|stemmingen?|termijnagenda|ter kennisneming|presentielijst|'
    r'vaststellen? (?:van )?(?:de |het )?(?:concept ?)?(?:agenda|notulen|verslag|besluitenlijst|actielijst)(?: \w+)?|vaststelling (?:van )?(?:de |het )?(?:concept ?)?(?:agenda|notulen|verslag|besluitenlijst)|'
    r'(?:conceptverslag|besluitenlijst|agenda|notulen|verslag)(?: van [\w \-]+)?|lijst van (?:openstaande )?toezeggingen.*|openstaande toezeggingen.*)'
    r'(?:\s+en\s+.*)?$')
PROC2=('uitzending','overlegvergadering','commissieplanning','daarbij betrekken','stemvenster','vaststelling van de agenda','bekrachtiging van de geheimhouding','inspre')   # titels zonder inhoud
def procedureel(t):
    t=re.sub(r'\s+',' ',fold(t)).strip(' .:;-')
    return not t or t in('algemeen','hoorzitting') or t.startswith(PROC2) or bool(PROC.match(t))

def needle(p):
    """Langste letterlijke stuk (>= 3 tekens, op diepte 0) van een patroonalternatief: moet in de gevouwen tekst staan, anders kan het patroon niet matchen.
    Alleen een snelle voorselectie (substring-test); de echte regex beslist. None = geen veilig stuk."""
    runs=[]; cur=''; depth=0; i=0
    def flush(nxt):
        nonlocal cur
        if cur:
            if nxt and nxt in '?*{': cur=cur[:-1]
            if len(cur)>=3: runs.append(cur)
        cur=''
    while i<len(p):
        c=p[i]
        if c=='\\': flush(''); i+=2; continue
        if c in '([': 
            if depth==0: flush('')
            depth+=1; i+=1
            if c=='[':
                while i<len(p) and p[i]!=']': i+=1
                depth-=1; i+=1
            continue
        if c==')': depth-=1; i+=1; continue
        if depth>0: i+=1; continue
        if c=='|': return None
        if c in '?*+{.^$': flush(c); i+=1; continue
        cur+=c; i+=1
    flush('')
    return max(runs,key=len) if runs else None
_G={}
def kandidaten(f):
    """Indexen van de patronen die in gevouwen tekst f kunnen voorkomen (voorselectie via letterlijke stukken)."""
    NS,NEED=_G['NS'],_G['NEED']
    hit={n for n in NS if n in f}
    return [q for q,nd in enumerate(NEED) if nd is None or not nd.isdisjoint(hit)]
def scan(p):
    """Eén blok debatteksten: per agendapunt de eerste videoseconde en per patroon het aantal treffers (draait in een werkproces)."""
    U,BL,apok,PR=_G['U'],_G['BL'],_G['apok'],_G['PR']
    i=int(os.path.basename(p)[:-4]); B=zload(p); res={}
    for j,beurt in enumerate(B):
        a=U[i*BL+j][0]
        if not apok[a]: continue
        e=res.get(a)
        if e is None: e=res[a]=[None,[0]*len(PR)]
        for sec,t in beurt:
            if sec is not None and sec>=0 and (e[0] is None or sec<e[0]): e[0]=sec
        f=fold(' '.join(t for _,t in beurt))
        for q in kandidaten(f):
            c=len(PR[q].findall(f))
            if c: e[1][q]+=c
    return res

def main():
    import time; T0=time.time()
    def tijd(w): print(f'  {w}: {time.time()-T0:.0f} s',flush=True)
    # ---------- bronnen ----------
    ST=zload(f'{DOCS}/data/ibabs/stukken.zst'); S=ST['soorten']; ROWS=ST['s']
    STAND=os.environ.get('RZ_STAND') or max(r[1] for r in ROWS)
    IDX=jload(f'{OUT}/d/index.json')['d']
    M=zload(f'{DOCS}/data/tekst/meta.zst'); L=zload(f'{DOCS}/data/tekst/labels.zst')
    DOM=L['dom']; GEB=L['geb']; DSL=[x[0] for x in DOM]
    guid={}
    for i,d in enumerate(M['d']):
        if d:
            m=re.search(r'/Item/([0-9a-f-]{36})',d[4] or '')
            if m: guid[m.group(1)]=i
    # stemuitslag/raadsvergadering per motie en amendement (via BB-nummer)
    VG={}
    km={}
    for key,bb in jload(f'{DOCS}/data/ibabs/moties.json').items():
        y,k=key.split(':'); km.setdefault(y,{})[int(k)]=bb
    for y,kk in km.items():
        Y=zload(f'{DOCS}/data/raad/{y}.zst')
        for k,bb in kk.items():
            m=Y['mo'][k]; mt=Y['M'][Y['s']['m'][m[0]]]
            VG[bb]={'d':mt[0],'stem':[m[4],m[5],m[6],m[7],m[8]]}
    # BB-nummer -> stuk (voorkeur voor een stuk dat geen motie/toezegging is: dat is de brief)
    BB={}
    for r in ROWS:
        if r[8]:
            b=r[8].lower()
            if b not in BB or (S[BB[b][0]] in('Motie','Toezegging') and S[r[0]] not in('Motie','Toezegging')): BB[b]=r
    # ---------- patronen per onderwerp/thema (volgorde van d/index.json) ----------
    pat={slug(n):onderwerpen.rx(pp) for n,pp in onderwerpen.actief()}; PRAW={slug(n):pp for n,pp in onderwerpen.actief()}
    pat.update({slug(n):onderwerpen.rx(pp) for n,pp,_ in onderwerpen.DWARS}); PRAW.update({slug(n):pp for n,pp,_ in onderwerpen.DWARS})
    for g in themes.T:
        for t in g[1]:
            if t[0]=='Parkeren': pat['parkeren']=rx_thema(t[1]); PRAW['parkeren']=[fold(x.strip().strip('"')) for x in t[1].split('|')]
    OND=[e for e in IDX if e['soort'] in('onderwerp','thema')]
    miss=[e['slug'] for e in OND if e['slug'] not in pat]
    if miss: print('GEEN PATROON voor',miss)
    OND=[e for e in OND if e['slug'] in pat]; PR=[pat[e['slug']] for e in OND]; OSL=[e['slug'] for e in OND]
    NEED=[]
    for e in OND:
        pp=PRAW[e['slug']]; ns=[needle(x) for x in pp]
        NEED.append(None if any(n is None for n in ns) else set(ns))
    _G.update(NEED=NEED,NS=sorted({n for nd in NEED if nd for n in nd}))
    # ---------- per stuk: onderwerpen ----------
    sond=[]; sdom=[]; sgeb=[]
    for r in ROWS:
        ft=fold(r[2]); fx=fold(r[6][:6000])
        sond.append([k for k in sorted(set(kandidaten(ft))|set(kandidaten(fx))) if PR[k].search(ft) or len(PR[k].findall(fx))>=3])
        i=guid.get(r[7]); sdom.append(L['d'][i] if i is not None else -1); sgeb.append(L['g'][i] if i is not None else 0)
    tijd('stukken en onderwerpen')
    # ---------- motie/toezegging: velden en stappen ----------
    def afd(r): return iso((re.search(r'afgedaan (\d\d-\d\d-\d{4})',r[5]) or [None,''])[1])
    def vw(r): return iso((re.search(r'verwacht (\d\d-\d\d-\d{4})',r[5]) or [None,''])[1])
    def effdatum(r): return VG[r[8]]['d'] if S[r[0]] in('Motie','Amendement') and r[8] in VG else r[1]
    def stappen(r):
        soort=S[r[0]]; st=[]
        if soort=='Motie':
            d0=effdatum(r); st.append([min(r[1],d0),'ingediend','Motie ingediend',''])   # registratiedatum = indiening; kan vóór de raadsvergadering liggen
            v=VG.get(r[8]); lab='Aangenomen'
            if v and v['stem'][1]>=0: lab=f"Aangenomen ({v['stem'][1]} voor, {v['stem'][2]} tegen)"
            if r[4] in(4,5,1): st.append([d0,'stemming',lab,''])
        else: st.append([r[1],'toegezegd','Toezegging gedaan',''])
        for dt,t,lab,bb in svz(r[6]):
            b=BB.get(bb) if bb else None
            st.append([dt,t,lab,b[7] if b and b is not r else ''])
        a=afd(r); v=vw(r)
        if a: st.append([a,'afgedaan','Afgedaan',''])
        elif v and r[4]==4: st.append([v,'verwacht','Afdoening verwacht',''])
        seen=set(); out=[]
        for s in sorted(st,key=lambda s:(s[0],VOLG[s[1]])):
            k=tuple(s)
            if k in seen: continue
            seen.add(k); out.append(s)
        return out
    ID2R={r[7]:r for r in ROWS}
    def ph(r,st):
        for t in('afdoeningsvoorstel','tussenbericht'):
            for s in reversed(st):
                if s[1]==t and s[3] and s[3] in ID2R:
                    w=zonder_wh(ID2R[s[3]][3])
                    if w: return w
        return ''
    # ---------- Uitvoer 1: beloofd.json / beloofd-af.json ----------
    def trk(r,st):
        mot=S[r[0]]=='Motie'; wie=r[3].strip()
        if mot: wie=re.split(r'\s*\(',wie,maxsplit=1)[0].strip()
        else: wie=zonder_wh(wie.split(' · ')[0]);
        com=r[3].split(' · ',1)[1].strip() if (not mot and ' · ' in r[3]) else ''
        if mot: tekst=motiekern(r[6]).get('v','')
        else: tekst=kort(re.sub(r'\s+',' ',r[6].split('\nStand van zaken')[0]).strip(),300) if r[6] else ''
        return mot,wie,com,tekst
    a24=datetime.date.fromisoformat(STAND);
    try: a24=a24.replace(year=a24.year-2)
    except ValueError: a24=a24.replace(year=a24.year-2,day=28)
    a24=a24.isoformat()
    kop={'stand':STAND,'dom':DOM,'geb':GEB,'ond':[[e['slug'],e['naam']] for e in OND],
         'kol':['soort','datum','titel','wie','commissie','dom','geb','status','verwacht','afgedaan','bb','id','tekst','stappen','stem','ond','ph']}
    lijsten={'open':[],'af':[]}; stap_cache={}
    for k,r in enumerate(ROWS):
        if S[r[0]] not in('Motie','Toezegging') or r[4] not in(4,5): continue
        a=afd(r)
        if r[4]==5 and not(a and a24<=a<=STAND): continue
        st=stappen(r); stap_cache[k]=st
        mot,wie,com,tekst=trk(r,st)
        row=[0 if mot else 1,effdatum(r),r[2],wie,com,sdom[k],sgeb[k],r[4],vw(r),a,r[8],r[7],tekst,st,VG[r[8]]['stem'] if mot and r[8] in VG else None,sond[k],ph(r,st) if mot else '']
        lijsten['open' if r[4]==4 else 'af'].append(row)
    ch=0
    for naam,key in(('beloofd.json','open'),('beloofd-af.json','af')):
        rs=sorted(lijsten[key],key=lambda x:(x[1],x[11]),reverse=True)
        ch+=schrijf(f'{OUT}/{naam}',dict(kop,r=rs)); print(naam,len(rs),'rijen')
    tijd('beloofd.json klaar')
    # ---------- Uitvoer 2: dossiertijdlijn ----------
    # stukken -> gebeurtenissen (eenmalig)
    TYPE={'Toezegging':('toez','c'),'Motie':('motie','r'),'Amendement':('amendement','r'),'Initiatiefvoorstel':('voorstel','r'),'Raadsvoorstel':('voorstel','c'),'Collegebesluit':('besluit','c'),
          'Collegebrief':('brief','c'),'Schriftelijke vragen':('vragen','r'),'Wijkraadadvies':('wijk','r'),'Ongevraagd wijkraadadvies':('wijk','r'),'Wijkakkoord of wijkplan':('wijk','r'),
          'Collegereactie op wijkplan':('wijk','r'),'Wijkverslag':('wijk','r'),'Rekenkamerrapport':('rapport','r'),'Ombudsman':('rapport','r')}
    EV=[]   # (stukindex, datum, type, kant, titel, sub, url, x) of afdoening
    for k,r in enumerate(ROWS):
        soort=S[r[0]]; typ,kant=TYPE[soort]; d=effdatum(r); wie=r[3].strip(); url=rl(r)
        x={}
        if soort in('Motie','Amendement'):
            fr=re.split(r'\s*\(',wie,maxsplit=1)[0].strip(); v=VG.get(r[8])
            if r[4] in(1,4,5): sub=fr+' · aangenomen'
            elif r[4]==2: sub=fr+' · verworpen'+(f" ({v['stem'][1]}–{v['stem'][2]})" if v and v['stem'][1]>=0 else '')
            elif r[4]==3: sub=fr+' · '+(r[5] or 'ingetrokken')
            else: sub=fr
            if r[4]: x['st']=r[4]
            if soort=='Motie':
                if vw(r): x['vw']=vw(r)
                if afd(r): x['af']=afd(r)
            if r[8]: x['bb']=r[8]
            if soort=='Motie' and r[4] in(4,5): x['stap']=stap_cache.get(k) or stappen(r)
        elif soort=='Toezegging':
            fn=zonder_wh(wie.split(' · ')[0]); a=afd(r); v=vw(r)
            sub=fn+' · '+(f'afgedaan {dk(a)}' if a else (f'open, verwacht {dk(v)}' if v else 'open' if r[4]==4 else r[5]))
            x['st']=r[4]
            if v and r[4]==4: x['vw']=v
            if a: x['af']=a
            if r[8]: x['bb']=r[8]
            x['stap']=stap_cache.get(k) or stappen(r)
        elif soort=='Schriftelijke vragen':
            fr=re.split(r'\s*\(',wie,maxsplit=1)[0].strip(); sub=(fr+' · ' if fr else '')+(r[5] or 'nog niet beantwoord')
        elif soort in('Rekenkamerrapport','Ombudsman'): sub=soort if soort=='Ombudsman' else 'Rekenkamer'
        elif soort in('Wijkraadadvies','Ongevraagd wijkraadadvies','Wijkakkoord of wijkplan','Collegereactie op wijkplan','Wijkverslag'): sub=(soort+(' · '+wie if wie else ''))
        else: sub=zonder_wh(wie) or ('College' if kant=='c' else '')
        EV.append((k,d,typ,kant,r[2],sub,url,x))
        a=afd(r)
        if soort in('Motie','Toezegging') and a and r[4]==5:
            EV.append((k,a,'afdoening','c',r[2],'Motie afgedaan' if soort=='Motie' else 'Toezegging afgedaan',url,{}))
    # agendapunten uit de debatten
    D=zload(f'{DOCS}/data/debat/meta.zst'); AP=D['ap']; VERG=D['verg']; U=D['u']; BL=D['blok']
    apok=[bool(a[2].strip()) and not procedureel(a[2]) for a in AP]
    aptel=collections.defaultdict(lambda:[None,[0]*len(PR)])
    apsp=collections.defaultdict(set)
    for u in U:
        if u[1]>=0: apsp[u[0]].add(u[1])
    bestanden=sorted(glob.glob(f'{DOCS}/data/debat/b/*.zst'))
    _G.update(U=U,BL=BL,apok=apok,PR=PR)
    try:
        import multiprocessing as mp
        with mp.get_context('fork').Pool(max(1,min(4,os.cpu_count() or 1))) as pool: delen=pool.map(scan,bestanden,chunksize=8)
    except Exception as ex:
        print('parallel scannen mislukt (',ex,'), een voor een'); delen=[scan(p) for p in bestanden]
    for res in delen:
        for a,(s,c) in res.items():
            e=aptel[a]
            if s is not None and (e[0] is None or s<e[0]): e[0]=s
            for q,n in enumerate(c): e[1][q]+=n
    tijd('debatten gescand')
    DE=[]   # (apindex, datum, titel, sub, url, x, ond-lijst)
    for a,ap in enumerate(AP):
        if not apok[a] or a not in apsp and a not in aptel: continue
        vg=VERG[ap[0]]; raad=vg[1]==0; naam=re.sub(r'\s*\(\d{4}\s*-\s*\d{4}\)$','',vg[2] or '') or ('Gemeenteraad' if raad else 'Commissie')
        n=len(apsp.get(a,()))
        sub=naam+(f' · {n} sprekers' if n!=1 else ' · 1 spreker') if n else naam
        x={}
        if vg[4]: x['v']=vg[4]
        s=aptel[a][0] if a in aptel else None
        if s is not None: x['s']=s
        if vg[3]: x['a']=vg[3]
        if ap[1]: x['n']=ap[1]
        if not raad: x['c']=1
        ft=fold(ap[2]); cnt=aptel[a][1] if a in aptel else [0]*len(PR)
        ol=[q for q,rr in enumerate(PR) if rr.search(ft) or cnt[q]>=3]
        DE.append((a,vg[0],re.sub(r'\s+',' ',ap[2]).strip(),sub,'https://gemeenteraad.rotterdam.nl/Agenda/Index/'+vg[3] if vg[3] else '',x,ol))
    # ---------- dossiers samenstellen ----------
    GSL=[slug(g) for g in GEB]
    leden=collections.defaultdict(lambda:{'s':[],'a':[]})
    sl_all={e['slug'] for e in IDX}
    def lid(sl,kind,i):
        if sl in sl_all: leden[sl][kind].append(i)
    for k,r in enumerate(ROWS):
        for q in sond[k]: lid(OSL[q],'s',k)
        d=sdom[k]; m=sgeb[k]
        if d>=0: lid(DSL[d],'s',k)
        for b,g in enumerate(GSL):
            if m>>b&1:
                lid(g,'s',k)
                if d>=0: lid(DSL[d]+'--'+g,'s',k)
    for j,(a,datum,titel,sub,url,x,ol) in enumerate(DE):
        ap=AP[a]
        for q in ol: lid(OSL[q],'a',j)
        d=ap[3]; m=ap[4]
        if d>=0: lid(DSL[d],'a',j)
        for b,g in enumerate(GSL):
            if m>>b&1:
                lid(g,'a',j)
                if d>=0: lid(DSL[d]+'--'+g,'a',j)
    sev=collections.defaultdict(list)
    for e in EV: sev[e[0]].append(e)
    os.makedirs(LIJN,exist_ok=True)
    telindex={}; overgeslagen=[]; soorten=collections.Counter(); afk=[]
    TELK={'debat':'debat','motie':'motie','amendement':'motie','toez':'toez','brief':'brief','besluit':'brief','vragen':'vragen','voorstel':'voorstel','rapport':'rapport','wijk':'wijk'}
    for e in IDX:
        sl=e['slug']; ond=e['soort'] in('onderwerp','thema'); sinds=2018 if ond else 2022; van=f'{sinds}-01-01'
        ev=[]; stukk=set(leden[sl]['s'])
        for k in leden[sl]['s']:
            for (_,d,typ,kant,titel,sub,url,x) in sev[k]:
                if d>=van: ev.append((d,typ,kant,titel,sub,url,x,k))
        for j in leden[sl]['a']:
            a,datum,titel,sub,url,x,ol=DE[j]
            if datum>=van and datum<=STAND: ev.append((datum,'debat','r',titel,sub,url,x,-1))
        # brieven die een stap zijn van een motie/toezegging in ditzelfde dossier
        bij={}
        for k in stukk:
            r=ROWS[k]
            if S[r[0]] in('Motie','Toezegging') and r[4] in(4,5):
                for s in stap_cache.get(k) or stappen(r):
                    if s[3] and s[1] in('afdoeningsvoorstel','tussenbericht'):
                        if s[3] not in bij or s[1]=='afdoeningsvoorstel': bij[s[3]]=(r[2],s[1])
        ev2=[]
        for (d,typ,kant,titel,sub,url,x,k) in ev:
            if k>=0 and typ=='brief' and ROWS[k][7] in bij:
                x=dict(x,bij=bij[ROWS[k][7]][0],stap=bij[ROWS[k][7]][1])
            ev2.append((d,typ,kant,titel,sub,url,x))
        ev2.sort(key=lambda t:(t[0],t[1],t[3],t[5]),reverse=True)
        if len(ev2)<3: overgeslagen.append(sl); continue
        tel={k:0 for k in('debat','motie','toez','brief','vragen','voorstel','rapport','wijk')}
        for t in ev2:
            if t[1] in TELK: tel[TELK[t[1]]]+=1
        o={'stand':STAND,'naam':e['naam'],'soort':e['soort'],'sinds':sinds,'tel':tel}
        if not ond and len(ev2)>1500: ev2=ev2[:1500]; o['afgekapt']=True; afk.append(sl)
        o['e']=[list(t) for t in ev2]; ch+=schrijf(f'{LIJN}/{sl}.json',o); telindex[sl]=len(ev2); soorten[e['soort']]+=1
    ch+=schrijf(f'{LIJN}/index.json',telindex)
    for p in glob.glob(f'{LIJN}/*.json'):   # verouderde bestanden (dossier weggevallen of te klein geworden)
        b=os.path.basename(p)[:-5]
        if b!='index' and b not in telindex: os.remove(p); ch+=1
    tijd('klaar')
    print('lijn:',len(telindex),'dossiers',dict(soorten),'| overgeslagen',len(overgeslagen),overgeslagen,'| afgekapt',afk,'| gewijzigd',ch,'bestanden')

if __name__=='__main__': main()
