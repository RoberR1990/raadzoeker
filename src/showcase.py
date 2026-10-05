# Extra's voor een voorbeelddossier (eerst Parkeren): de keten gezegd -> besloten -> beloofd -> gedaan, de stad in beeld, bron één klik.
#   python src/showcase.py [slug ...]   -> docs/ontwerp/d/<slug>-extra.json (zonder argument: alle voorbeelddossiers in CONFIG)
# Onderdelen
#   sub        subthema's (themes.py) met per subthema de regex; elk item krijgt de subthema's waar het over gaat
#   spoor      beloftespoor per motie/toezegging sinds 2022: ingediend/toegezegd -> tussenberichten -> afdoeningsvoorstel -> afgedaan (iBabs 'Stand van zaken')
#   vastgesteld  verordeningen, tarieven en beleidsregels uit het Gemeenteblad (geen losse verkeersbesluiten)
#   komt       wat eraan komt: open toezeggingen/moties met een verwachte datum na de stand, raadsvoorstellen die nog behandeld worden
#   wijken     per wijk: wijkraadstukken, verkeersbesluiten en raadsstukken over parkeren, (geen autobezit: besluit Robert, te veel nadruk op één indicator)
#   stemmen    stemgedrag per fractie op parkeermoties sinds 2022 (hoofdelijke stemmingen uit de notulen)
#   debatten   debatfragmenten (raad en commissies, 2022+) met het videomoment
import json,os,re,glob,collections
from paden import WERK,DOCS,STAND
from ontwerp_data import zload,iso,kort,motiekern,rx,fold
import themes, teksten as T

# Per voorbeelddossier: naam, slug van het dossier, zoekpatroon (op gevouwen tekst), subthema's (naam, termen) en verwante dossiers.
CONFIG={
 'parkeren':dict(naam='Parkeren',rx=r'parkeer|parkeren|parkeert|geparkeerd|naheffing|scanauto|bewonersvergunning|bezoekersregeling',sub='themes:Parkeren',verwant=[],domein='mobiliteit'),
 'handhaving-en-toezicht':dict(naam='Handhaving en toezicht',
   rx=r"handhav|boa|boa's|toezichthouder|stadswacht|bestuurlijke boete|bestuurlijke strafbeschikking|last onder dwangsom|bodycam",
   sub=[("Handhavers en boa's","handhavers | boa | stadswacht | toezichthouder | stadsmarinier"),
        ('Overlast en openbare orde','overlast | openbare orde | gebiedsverbod | noodverordening | samenscholing | hangjongeren'),
        ('Afval en vervuiling','afval | zwerfvuil | bijplaatsing | grofvuil | dumping'),
        ('Parkeren en verkeer','parkeer | naheffing | scanauto | verkeershandhaving'),
        ('Wonen en verhuur','huisjesmelk | verhuurder | woonfraude | onrechtmatige bewoning | kamerverhuur | illegale verhuur | vakantieverhuur'),
        ('Horeca en evenementen','horeca | terras | sluitingstijd | evenement'),
        ('Drugs en sluitingen','damocles | drugs | sluiting | ondermijning | lachgas'),
        ('Middelen en bevoegdheden','camera | bodycam | fouilleren | bestuurlijke strafbeschikking | bestuurlijke boete | last onder dwangsom | geweld tegen | wapenstok | bevoegdhe')],
   verwant=['cameratoezicht','jongerenoverlast-en-jeugdcriminaliteit','lachgas','afval-zwerfvuil-en-grofvuil','goed-verhuurderschap-en-huisjesmelkers','horeca-terrassen-en-nachtleven','parkeren','ondermijning-en-drugscriminaliteit'],domein='veiligheid'),
}
CONFIG['wonen-en-bouwen']=dict(naam='Wonen en bouwen',label='wonen',   # domein: selectie op domeinlabel (fase 1), niet op zoekwoord
   rx=r'woning|huurder|huurwoning|woonvisie|corporatie|nieuwbouw|woningbouw|bestemmingsplan|omgevingsplan|omgevingsvisie|gebiedsontwikkeling|sloop|middenhuur|sociale huur|verhuur|huisjesmelk|leegstand|erfpacht|hoogbouw|verdicht',
   sub='themes:Wonen+Bouwen & ruimte',verwant=[],domein='wonen',
   vergunning=('^omgevingsvergunning$','kap|standplaats','Omgevingsvergunningen','aangevraagd en verleend, per jaar (bekendmakingen; geen kapvergunningen)'),
   cbs=[('huur','Huurwoningen (%)'),('corp','Corporatiewoningen (%)'),('woz','WOZ-waarde (× € 1.000)')],
   projecten=[('Feyenoord City en Stadionpark',r'feyenoord city|stadionpark'),('Merwe-Vierhavens (M4H)',r'merwe.?vierhaven|\bm4h\b'),('Rijnhaven',r'rijnhaven'),
     ('Hart van Zuid',r'hart van zuid'),('Tweebosbuurt',r'tweebos'),('Pompenburg',r'pompenburg'),('Nieuw Kralingen',r'nieuw kralingen'),('Wielewaal',r'wielewaal'),
     ('Nieuw-Crooswijk',r'nieuw.crooswijk'),('Centraal District en Weena',r'centraal district|\bweena\b'),('Bospolder-Tussendijken',r'bospolder.tussendijken|\bbotu\b'),('Kop van Zuid',r'kop van zuid')])
CONFIG['zorg-welzijn-en-jeugd']=dict(naam='Zorg, welzijn en jeugd',label='zorg',
   rx=r'jeugdzorg|jeugdhulp|wmo|welzijn|mantelzorg|ouderen|eenzaam|huisarts|ggd|wijkteam|zorg|dagbesteding|huishoudelijke hulp|gezondheid|preventie|dakloo',
   sub='themes:Zorg, welzijn & jeugd',verwant=['jeugdhulp','wmo-en-hulp-bij-het-huishouden','doelgroepenvervoer','dakloosheid-en-daklozenopvang'],domein='zorg',
   cbs=[('oud','65 jaar en ouder (%)'),('jong','Kinderen tot 15 jaar (%)'),('eenp','Eenpersoonshuishoudens (%)')])
CONFIG['economie-en-haven']=dict(naam='Economie en haven',label='economie',
   rx=r'haven|ondernemer|economie|horeca|werkgelegenheid|winkel|\bmkb\b|toeris|hotel|bedrijventerrein|industrie|startup|nachtleven|markt',
   sub='themes:Economie & haven',verwant=['horeca-terrassen-en-nachtleven','rotterdam-the-hague-airport','walstroom-en-haven-uitstoot'],domein='economie',
   vergunning=('exploitatievergunning','','Horecavergunningen','exploitatievergunningen, aangevraagd en verleend, per jaar (bekendmakingen)'),
   projecten=[('Merwe-Vierhavens (M4H)',r'merwe.?vierhaven|\bm4h\b'),('RDM en Heijplaat',r'\brdm\b'),('Ahoy',r'\bahoy\b'),('Markthal en Binnenrotte',r'markthal|binnenrotte'),
     ('Zuidplein',r'zuidplein'),('Lijnbaan',r'lijnbaan'),('Hart van Zuid',r'hart van zuid'),('Witte de Withstraat',r'witte de with'),('Rotterdam The Hague Airport',r'rotterdam the hague airport|\brtha\b','noordkethel-schieveen-zestienhoven'),
     ('Katendrecht',r'katendrecht'),('Waalhaven',r'waalhaven'),('Nieuwe Binnenweg',r'nieuwe binnenweg')])
NAAM=SLUG=None; RX=None; CFG=None
DATUM=r'(\d{1,2})-(\d{1,2})-(\d{4})'
def d_iso(s):
    m=re.search(DATUM,s or ''); return f'{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}' if m else ''
def jl(p):
    for l in open(p,encoding='utf8'):
        try: yield json.loads(l)
        except ValueError: pass

def main(slug='parkeren'):
    global NAAM,SLUG,RX,CFG
    CFG=CONFIG[slug]; NAAM=CFG['naam']; SLUG=slug; RX=re.compile(CFG['rx'])
    if isinstance(CFG['sub'],str):
        SUB=[]
        for naam in CFG['sub'].split(':')[1].split('+'):
            th=next(t for g in themes.T for t in g[1] if t[0]==naam); SUB+=[(n,rx(t)) for n,t in th[2] if n!='Dak- en thuisloosheid' or naam!='Wonen' or 'label' not in CFG]
    else: SUB=[(n,rx(t)) for n,t in CFG['sub']]
    def subs(t): f=fold(t); return [n for n,r in SUB if r.search(f)]
    W=os.path.join(WERK,'ibabs')
    LD=json.load(open(os.path.join(WERK,'labels','domein.json'),encoding='utf8')) if CFG.get('label') else {}
    INFO0=json.load(open(os.path.join(WERK,'labels','info.json'),encoding='utf8')) if CFG.get('label') else {}
    item2k={}
    for k,v in INFO0.items():
        m=re.search(r'/Item/([0-9a-f-]{36})',v[4] or '')
        if m: item2k[m.group(1)]=k
    def hoort(item_id,titel,tekst):
        if CFG.get('label'): return LD.get(item2k.get(item_id),[None])[0]==CFG['label']
        return bool(RX.search(fold(titel)) or len(RX.findall(fold(tekst)))>=2)
    # brieven op bb-nummer (voor de schakels in het spoor)
    brief={}
    for r in jl(os.path.join(W,'items_brieven.jsonl')):
        d=r['detail']; bb=d.get('BB-nummer') or (r.get('lijst') or {}).get('externalid')
        if bb: brief[bb.lower()]=(d.get('Titel',''),'https://gemeenteraad.rotterdam.nl/Reports/Item/'+r['id'])
    STEM={}
    for key,bb in json.load(open(os.path.join(DOCS,'data','ibabs','moties.json'))).items():
        y,k=key.split(':'); STEM.setdefault(y,{})[int(k)]=bb
    for y,kk in list(STEM.items()):
        Y=zload(os.path.join(DOCS,'data','raad',f'{y}.zst'))
        for k,bb in kk.items(): m=Y['mo'][k]; STEM[bb]=[m[4],m[5],m[6],m[7],m[8]]
        del STEM[y]
    def stappen(d,soort):
        st=[]
        if soort=='motie':
            st.append([d_iso(d.get('Datum ingediend') or d.get('Datum ontvangen')),'ingediend','Motie ingediend',None])
            if d.get('Uitslag'): st.append([d_iso(d.get('Datum ingediend') or d.get('Datum ontvangen')),'stemming',d['Uitslag'],None])
        else: st.append([d_iso(d.get('Datum toezegging')),'toegezegd','Toezegging gedaan',None])
        for part in re.split(r'[\r\n;]+',d.get('Stand van zaken') or ''):
            m=re.match(r'\s*([A-Za-z ]+?)\s*:?\s*'+DATUM+r'(?:\s*\(([^)]*)\))?',part)
            if not m: continue
            wat=m.group(1).strip().lower(); dt=f'{m.group(4)}-{int(m.group(3)):02d}-{int(m.group(2)):02d}'
            bb=re.search(r'\d{2}bb\d+',m.group(5) or '',re.I); b=brief.get(bb.group(0).lower()) if bb else None
            soort2='tussenbericht' if 'tussen' in wat or 'voortgang' in wat else 'afdoeningsvoorstel' if 'afdoening' in wat else 'commissieadvies' if 'commissie' in wat else 'overig'
            st.append([dt,soort2,{'tussenbericht':'Tussenbericht van het college','afdoeningsvoorstel':'Afdoeningsvoorstel van het college','commissieadvies':'Advies van de commissie'}.get(soort2,m.group(1).strip()),b[1] if b else None])
        if d.get('Datum afgedaan'): st.append([d_iso(d['Datum afgedaan']),'afgedaan','Afgedaan',None])
        elif d.get('Verwachte datum afdoening'): st.append([d_iso(d['Verwachte datum afdoening']),'verwacht','Afdoening verwacht',None])
        return sorted([s for s in st if s[0]],key=lambda s:s[0])
    spoor=[]
    for f,soort in(('items_moties.jsonl','motie'),('items_toezeggingen.jsonl','toezegging')):
        for r in jl(os.path.join(W,f)):
            d=r['detail']; tit=d.get('Titel') or ''; tekst=r.get('tekst') or d.get('Omschrijving') or ''
            if not hoort(r['id'],tit,tekst): continue
            datum=d_iso(d.get('Datum ingediend') or d.get('Datum ontvangen') or d.get('Datum toezegging'))
            if datum<'2022': continue
            if soort=='motie' and not re.search(r'aangenomen|geamendeerd',d.get('Uitslag') or '',re.I): continue
            wie=d.get('Partij') or d.get('Portefeuillehouder') or ''
            bb=d.get('BB nummer') or d.get('BB-nummer') or ''
            x={'soort':soort,'datum':datum,'titel':tit,'wie':re.sub(r'\s*\(.*','',wie),'url':'https://gemeenteraad.rotterdam.nl/Reports/Item/'+r['id'],
               'open':not d.get('Datum afgedaan'),'sub':subs(tit+' '+tekst),'stappen':stappen(d,soort)}
            if soort=='motie':
                k=motiekern(tekst); x.update({'verzoek':k.get('v',''),'stem':STEM.get(bb)})
            else: x['toezegging']=kort(re.sub(r'\s+',' ',d.get('Omschrijving') or ''),260)
            spoor.append(x)
    spoor.sort(key=lambda x:x['datum'],reverse=True)
    if CFG.get('label'):   # een heel domein: alles wat open is, plus de 200 nieuwste afgedane (anders wordt de pagina te zwaar)
        af=[x for x in spoor if not x['open']]; spoor=[x for x in spoor if x['open'] or x in af[:200]]
    # vastgesteld: Gemeenteblad
    bm=[b for b in jl(os.path.join(WERK,'wijk','bekendmakingen.jsonl'))]
    regels={}
    for i,b in enumerate(bm):
        if not RX.search(fold(b['titel'])) or not re.search(r'verordening|beleidsregel|algemene strekking',b['type'],re.I): continue   # regels, geen losse beschikkingen
        sleutel=re.sub(r'\b(20\d\d|wijziging|tweede|derde|eerste)\b','',b['titel'].lower()); sleutel=re.sub(r'\W+',' ',sleutel).strip()
        if sleutel not in regels or b['d']>regels[sleutel]['datum']:
            regels[sleutel]={'datum':b['d'],'titel':b['titel'],'soort':b['type'],'url':b['url'],'n':regels.get(sleutel,{}).get('n',0)+1,'sub':subs(b['titel'])}
        else: regels[sleutel]['n']+=1
    vast=sorted(regels.values(),key=lambda x:x['datum'],reverse=True)
    # komt eraan
    komt=[x for x in spoor if x['open'] and x['stappen'] and x['stappen'][-1][1]=='verwacht' and x['stappen'][-1][0]>=STAND]
    komt=sorted(komt,key=lambda x:x['stappen'][-1][0])[:12]
    rv=[]
    for r in jl(os.path.join(W,'items_raadsvoorstellen.jsonl')):
        d=r['detail']; tit=d.get('Titel') or ''
        if not hoort(r['id'],tit,''): continue
        beh=d.get('Behandeladvies') or ''; dd=d_iso(beh)
        if dd and dd>=STAND or d_iso(d.get('Datum ontvangen'))>=STAND[:4]+'-08-01':
            rv.append({'datum':d_iso(d.get('Datum ontvangen')),'titel':tit,'behandeling':beh,'url':'https://gemeenteraad.rotterdam.nl/Reports/Item/'+r['id'],'sub':subs(tit)})
    # wijken
    LG=json.load(open(os.path.join(WERK,'labels','gebied.json'),encoding='utf8'))
    INFO=json.load(open(os.path.join(WERK,'labels','info.json'),encoding='utf8'))
    WK=json.load(open(os.path.join(DOCS,'ontwerp','wijken.json'),encoding='utf8'))['wijken']
    tel={w['slug']:collections.Counter() for w in WK}
    vb=collections.defaultdict(list)
    for k,v in LG.items():
        if k.startswith('b:'):
            b=bm[int(k[2:])]
            if not RX.search(fold(b['titel'])): continue
            for w,meth,n in v:
                if w in tel: tel[w]['verkeersbesluit' if b['type'].startswith('verkeersbesluit') else 'besluit']+=1; vb[w].append([b['d'],b['titel'][:140],b['url']])
        elif k in INFO:
            s,d,tit,wie,url=INFO[k]
            if CFG.get('label'):
                if LD.get(k,[None])[0]!=CFG['label']: continue
            elif not tit or not RX.search(fold(tit)): continue
            soort='wijkraad' if s.startswith(('Wijk','Ongevraagd')) else 'raad'
            for w,meth,n in v:
                if w in tel: tel[w][soort]+=1
    vg=collections.defaultdict(collections.Counter)   # omgevingsvergunningen per wijk per jaar (geen kap- of standplaatsvergunningen)
    if CFG.get('vergunning'):
        vt,vx=CFG['vergunning'][0],CFG['vergunning'][1]
        for k,v in LG.items():
            if not k.startswith('b:'): continue
            b=bm[int(k[2:])]
            if not re.search(vt,b['type']) or (vx and re.search(vx,b['titel'],re.I)): continue
            for w,meth,n in v:
                if w in tel: vg[w][b['d'][:4]]+=1
    wijken=[]
    for w in WK:
        c=w['cbs'].get('2024') or w['cbs'].get('2023') or {}
        x={'slug':w['slug'],'naam':w['naam'],'gebied':w['gebied'],'n':dict(tel[w['slug']]),'recent':sorted(vb[w['slug']],reverse=True)[:3]}
        x.update({'lx':w.get('lx'),'ly':w.get('ly')})
        if CFG.get('vergunning'): x['vg']=dict(vg[w['slug']])
        for key,_ in CFG.get('cbs',[]): x[key]=c.get(key)
        wijken.append(x)
    # grote projecten: waar (wijk die de stukken het vaakst noemen) en wat er over gezegd is
    projecten=[]
    if CFG.get('projecten'):
        import domeinen as DM
        m_,tekst_=DM.tekstdocs(); S_=m_['soorten']; WS={w['slug']:w for w in WK}
        for pnaam,prx,*vaste_wijk in CFG['projecten']:   # derde element: vaste wijk als de stukken een andere plek noemen
            r_=re.compile(prx); docs=[]; wt=collections.Counter()
            for i,r in enumerate(m_['d']):
                if r_.search(fold(r[2])) or (r[5] and r[5]<3000 and len(r_.findall(fold(tekst_(i))))>=2):
                    docs.append([r[1],S_[r[0]],r[2][:140],r[4]])
                    for w,meth,n in LG.get(f't:{i}',[]):
                        if w in WS: wt[w]+=1
            if not docs or not wt: continue
            w0=vaste_wijk[0] if vaste_wijk else wt.most_common(1)[0][0]; docs.sort(reverse=True)
            projecten.append({'naam':pnaam,'wijk':w0,'wijknaam':WS[w0]['naam'],'lx':WS[w0]['lx'],'ly':WS[w0]['ly'],'n':len(docs),
                              'per':dict(collections.Counter(d[0][:4] for d in docs)),'recent':docs[:5],'zoek':pnaam.split(' (')[0]})
    # stemgedrag per fractie (moties sinds 2022 met hoofdelijke stemming)
    meta=json.load(open(os.path.join(DOCS,'data','raad','meta.json'),encoding='utf8')); PAR=meta['par']
    aanwezig=collections.defaultdict(set)
    for p in glob.glob(os.path.join(DOCS,'data','raad','202[2-6].zst')):
        Y=zload(p); y=os.path.basename(p)[:4]
        for j,pa in enumerate(Y['s']['pa']):
            if pa>=0: aanwezig[y].add(PAR[pa]); aanwezig[Y['M'][Y['s']['m'][j]][0]].add(PAR[pa])   # per jaar en per vergaderdag
    stem=collections.defaultdict(lambda:[0,0]); nst=0; tabel=[]   # tabel: per motie hoe elke fractie stemde
    for r in jl(os.path.join(W,'items_moties.jsonl')):
        d=r['detail']; tit=d.get('Titel') or ''; datum=d_iso(d.get('Datum ingediend') or d.get('Datum ontvangen'))
        bb=d.get('BB nummer') or ''
        if datum<'2022' or not hoort(r['id'],tit,'') or bb not in STEM: continue
        aan,voor,tegen,zijde,fr=STEM[bb]
        if voor<0 or not fr: continue
        dag=datum if datum in aanwezig else next((d for d in sorted(k for k in aanwezig if len(k)==10 and k>=datum)[:1]),datum[:4])   # fracties die die vergaderdag spraken
        genoemd={p for p in aanwezig[dag] if re.search(r'(?<![\w])'+re.escape(p)+r'(?![\w])',fr)}
        if not genoemd: continue
        nst+=1; per={}
        for p in aanwezig[dag]:
            v=(p in genoemd)==(zijde=='v'); stem[p][0 if v else 1]+=1; per[p]='v' if v else 't'
        tabel.append([datum,tit,'https://gemeenteraad.rotterdam.nl/Reports/Item/'+r['id'],1 if aan else 0,per,subs(tit+' '+(r.get('tekst') or ''))])
    stemmen={'n':nst,'fracties':sorted([[p,a,b] for p,(a,b) in stem.items() if a+b>=5],key=lambda x:-x[1]/(x[1]+x[2])),'tabel':sorted(tabel,reverse=True)[:60]}
    # debatten met videomoment (raad en commissies, 2022+)
    deb={}
    for bron in('raad','commissies'):
        meta=json.load(open(os.path.join(DOCS,'data',bron,'meta.json'),encoding='utf8')); SPK=meta['spk']; PA=meta['par']
        for p in sorted(glob.glob(os.path.join(DOCS,'data',bron,'202[2-6].zst'))):
            Y=zload(p); S=Y['s']; yy=os.path.basename(p)[:4]; pre='r' if bron=='raad' else 'c'
            for i,t in enumerate(S['t']):
                if S['k'][i] not in(0,4) or not t: continue
                if CFG.get('label') and LD.get(f'{pre}:{yy}:{S["i"][i]}',[None])[0]!=CFG['label']: continue
                h=len(RX.findall(fold(t)))
                if not h: continue
                M=Y['M'][S['m'][i]]; I=Y['I'][S['i'][i]]; key=(M[0],M[1],I[1])
                e=deb.setdefault(key,{'datum':M[0],'verg':'Gemeenteraad' if bron=='raad' else re.sub(r'\s*\(.*','',M[2]),'punt':re.sub(r'\s+',' ',I[2])[:150],
                    'agenda':M[1],'n':0,'best':None,'sprekers':collections.Counter(),'sub':collections.Counter()})
                e['n']+=h
                wie=SPK[S['sp'][i]][0] if S['sp'][i]>=0 else ''; pa=PA[S['pa'][i]] if S['pa'][i]>=0 else ''
                if wie: e['sprekers'][wie+(f' ({pa})' if pa else '')]+=h
                for n in subs(t): e['sub'][n]+=1
                if not e['best'] or h>e['best'][0]:
                    m=RX.search(fold(t)); a=max(0,m.start()-160); b=min(len(t),m.end()+220)
                    e['best']=(h,('…' if a else '')+re.sub(r'\s+',' ',t[a:b]).strip()+('…' if b<len(t) else ''),wie,pa,M[4] if len(M)>4 else '',S['v'][i],S['k'][i]==4)
    top=sorted(deb.values(),key=lambda e:-e['n'])[:40]
    debatten=[{'datum':e['datum'],'verg':e['verg'],'punt':e['punt'],'agenda':e['agenda'],'n':e['n'],'fragment':e['best'][1],'wie':e['best'][2],'partij':e['best'][3],
               'video':e['best'][4] if e['best'][5] is not None and e['best'][5]>=0 else '','sec':e['best'][5],'auto':e['best'][6],
               'sprekers':[n for n,_ in e['sprekers'].most_common(4)],'sub':[n for n,_ in e['sub'].most_common(2)]} for e in sorted(top,key=lambda e:e['datum'],reverse=True)]
    import akkoord
    akk={'titel':akkoord.TITEL,'url':akkoord.URL,'domein':CFG['domein'],'passages':akkoord.passages(CFG['rx'])}   # letterlijk uit het coalitieakkoord
    uit={'naam':NAAM,'stand':STAND,'verwant':CFG['verwant'],'akkoord':akk,'sub':[n for n,_ in SUB],'spoor':spoor,'vastgesteld':vast,'komt':komt,'voorstellen':rv,'wijken':wijken,'stemmen':stemmen,'debatten':debatten,'projecten':projecten,
         'lagen':([['n','In de raad en wijkraden','stukken en debatten over dit domein die de wijk noemen of uit de wijk komen']]+
                  ([['vg',CFG['vergunning'][2],CFG['vergunning'][3]]] if CFG.get('vergunning') else [])+
                  [[k,n,'CBS 2024, ter vergelijking'] for k,n in CFG.get('cbs',[])]) if (CFG.get('vergunning') or CFG.get('cbs')) else []}
    p=os.path.join(DOCS,'ontwerp','d',SLUG+'-extra.json'); json.dump(uit,open(p,'w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
    print('spoor',len(spoor),'open',sum(x['open'] for x in spoor),'vastgesteld',len(vast),'komt',len(komt),'voorstellen',len(rv),'stemmingen',nst,'debatten',len(debatten),os.path.getsize(p)//1000,'kB')

if __name__=='__main__':
    import sys
    for a in (sys.argv[1:] or list(CONFIG)): main(a)
