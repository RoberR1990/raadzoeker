# Extra's voor een voorbeelddossier (eerst Parkeren): de keten gezegd -> besloten -> beloofd -> gedaan, de stad in beeld, bron één klik.
#   python src/showcase.py   -> docs/ontwerp/d/parkeren-extra.json
# Onderdelen
#   sub        subthema's (themes.py) met per subthema de regex; elk item krijgt de subthema's waar het over gaat
#   spoor      beloftespoor per motie/toezegging sinds 2022: ingediend/toegezegd -> tussenberichten -> afdoeningsvoorstel -> afgedaan (iBabs 'Stand van zaken')
#   vastgesteld  verordeningen, tarieven en beleidsregels uit het Gemeenteblad (geen losse verkeersbesluiten)
#   komt       wat eraan komt: open toezeggingen/moties met een verwachte datum na de stand, raadsvoorstellen die nog behandeld worden
#   wijken     per wijk: wijkraadstukken, verkeersbesluiten en raadsstukken over parkeren, plus autobezit (CBS) ter vergelijking
#   stemmen    stemgedrag per fractie op parkeermoties sinds 2022 (hoofdelijke stemmingen uit de notulen)
#   debatten   debatfragmenten (raad en commissies, 2022+) met het videomoment
import json,os,re,glob,collections
from paden import WERK,DOCS,STAND
from ontwerp_data import zload,iso,kort,motiekern,rx,fold
import themes, teksten as T

NAAM='Parkeren'; SLUG='parkeren'
RX=re.compile(r'parkeer|parkeren|parkeert|geparkeerd|naheffing|scanauto|bewonersvergunning|bezoekersregeling')
DATUM=r'(\d{1,2})-(\d{1,2})-(\d{4})'
def d_iso(s):
    m=re.search(DATUM,s or ''); return f'{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}' if m else ''
def jl(p):
    for l in open(p,encoding='utf8'):
        try: yield json.loads(l)
        except ValueError: pass

def main():
    th=next(t for g in themes.T for t in g[1] if t[0]==NAAM)
    SUB=[(n,rx(t)) for n,t in th[2]]
    def subs(t): f=fold(t); return [n for n,r in SUB if r.search(f)]
    W=os.path.join(WERK,'ibabs')
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
            if not (RX.search(fold(tit)) or len(RX.findall(fold(tekst)))>=2): continue
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
    # vastgesteld: Gemeenteblad
    bm=[b for b in jl(os.path.join(WERK,'wijk','bekendmakingen.jsonl'))]
    regels={}
    for i,b in enumerate(bm):
        if not RX.search(fold(b['titel'])) or b['type'].startswith('verkeersbesluit') or b['type']=='omgevingsvergunning': continue
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
        if not RX.search(fold(tit)): continue
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
            if not tit or not RX.search(fold(tit)): continue
            soort='wijkraad' if s.startswith(('Wijk','Ongevraagd')) else 'raad'
            for w,meth,n in v:
                if w in tel: tel[w][soort]+=1
    wijken=[]
    for w in WK:
        c=w['cbs'].get('2024') or w['cbs'].get('2023') or {}
        wijken.append({'slug':w['slug'],'naam':w['naam'],'gebied':w['gebied'],'n':dict(tel[w['slug']]),'auto':c.get('auto'),'inw':c.get('inw'),
                       'recent':sorted(vb[w['slug']],reverse=True)[:3]})
    # stemgedrag per fractie (moties sinds 2022 met hoofdelijke stemming)
    meta=json.load(open(os.path.join(DOCS,'data','raad','meta.json'),encoding='utf8')); PAR=meta['par']
    aanwezig=collections.defaultdict(set)
    for p in glob.glob(os.path.join(DOCS,'data','raad','202[2-6].zst')):
        Y=zload(p); y=os.path.basename(p)[:4]
        for pa in Y['s']['pa']:
            if pa>=0: aanwezig[y].add(PAR[pa])
    stem=collections.defaultdict(lambda:[0,0]); nst=0
    for r in jl(os.path.join(W,'items_moties.jsonl')):
        d=r['detail']; tit=d.get('Titel') or ''; datum=d_iso(d.get('Datum ingediend') or d.get('Datum ontvangen'))
        bb=d.get('BB nummer') or ''
        if datum<'2022' or not RX.search(fold(tit)) or bb not in STEM: continue
        aan,voor,tegen,zijde,fr=STEM[bb]
        if voor<0 or not fr: continue
        genoemd={p for p in aanwezig[datum[:4]] if re.search(r'(?<![\w])'+re.escape(p)+r'(?![\w])',fr)}
        if not genoemd: continue
        nst+=1
        for p in aanwezig[datum[:4]]:
            v=(p in genoemd)==(zijde=='v'); stem[p][0 if v else 1]+=1
    stemmen={'n':nst,'fracties':sorted([[p,a,b] for p,(a,b) in stem.items() if a+b>=5],key=lambda x:-x[1]/(x[1]+x[2]))}
    # debatten met videomoment (raad en commissies, 2022+)
    deb={}
    for bron in('raad','commissies'):
        meta=json.load(open(os.path.join(DOCS,'data',bron,'meta.json'),encoding='utf8')); SPK=meta['spk']; PA=meta['par']
        for p in sorted(glob.glob(os.path.join(DOCS,'data',bron,'202[2-6].zst'))):
            Y=zload(p); S=Y['s']
            for i,t in enumerate(S['t']):
                if S['k'][i] not in(0,4) or not t: continue
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
    uit={'naam':NAAM,'stand':STAND,'sub':[n for n,_ in SUB],'spoor':spoor,'vastgesteld':vast,'komt':komt,'voorstellen':rv,'wijken':wijken,'stemmen':stemmen,'debatten':debatten}
    p=os.path.join(DOCS,'ontwerp','d',SLUG+'-extra.json'); json.dump(uit,open(p,'w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
    print('spoor',len(spoor),'open',sum(x['open'] for x in spoor),'vastgesteld',len(vast),'komt',len(komt),'voorstellen',len(rv),'stemmingen',nst,'debatten',len(debatten),os.path.getsize(p)//1000,'kB')

if __name__=='__main__': main()
