# Wijken (71, indeling Wijkprofiel Rotterdam) -> docs/wijken.json en wijkkaart.json
# Per wijk: CBS-buurten (kaart, kerncijfers 2022-2025), Wijkprofiel-indexen 2014-2026, vermeldingen in de raad per jaar
# (wijknamen herkend in spreekbeurten), onderwerpen in dezelfde spreekbeurten, moties/toezeggingen/vragen die de wijk noemen.
# Bronnen in WERK: wijk/wijken.json (namen), wijk/wijkprofiel.json, kaart/buurten_JAAR.json (PDOK CBS).
import json,os,re,collections,unicodedata,glob,math,zstandard
from paden import WERK,DOCS,STAND
import themes
def fold(s): return ''.join(c for c in unicodedata.normalize('NFD',s.lower()) if unicodedata.category(c)!='Mn').replace('’',"'")
def n(s): return re.sub(r'[^a-z0-9]+',' ',fold(s)).strip()
GEBNAAM={'rotterdam-centrum':'Centrum','hoek-van-holland':'Hoek van Holland','hillegersberg-schiebroek':'Hillegersberg-Schiebroek','kralingen-crooswijk':'Kralingen-Crooswijk','prins-alexander':'Prins Alexander','ijsselmonde':'IJsselmonde'}
# zoeknamen per wijk; None = te dubbelzinnig (zelfde naam als het gebied, of een gewoon woord): alleen via het gebied
ZOEK={'delfshaven-wijk':None,'feijenoord-wijk':None,'overschie-wijk':None,'pernis-wijk':None,'rozenburg-wijk':None,'dorprijnpoort':['rijnpoort'],
 'strand-en-duin':None,'cool':['Cool'],'hillegersberg-noord':['hillegersberg-noord','hillegersberg noord'],'hillegersberg-zuid':['hillegersberg-zuid','hillegersberg zuid'],
 'kop-van-zuid':['kop van zuid'],'kop-van-zuid-entrepot':['entrepot'],'groot-ijsselmonde-noord':['groot ijsselmonde','groot-ijsselmonde'],'groot-ijsselmonde-zuid':['groot ijsselmonde','groot-ijsselmonde'],
 'oudmathenessewitte-dorp':['oud mathenesse','oud-mathenesse','witte dorp'],'blijdorpblijdorpsepolder':['re:(?<!diergaarde )(?<!diergaarde-)blijdorp'],'kralingen-oostkralingse-bos':['kralingen-oost','kralingen oost','kralingse bos'],
 'noordkethel-schieveen-zestienhoven':['noord kethel','noordkethel','schieveen','zestienhoven','landzicht'],'nieuwe-werkdijkzigt':['nieuwe werk','dijkzigt'],
 'zuiderpark-en-zuidrand':['zuiderpark','zuidrand'],'s-gravenland':["'s-gravenland","s-gravenland"],'oud-charlois':['oud-charlois','oud charlois'],'oud-crooswijk':['oud-crooswijk','oud crooswijk'],
 'nieuw-crooswijk':['nieuw-crooswijk','nieuw crooswijk'],'oud-ijsselmonde':['oud-ijsselmonde','oud ijsselmonde'],'kralingen-west':['kralingen-west','kralingen west'],'cs-kwartier':['cs-kwartier','cs kwartier','centraal district'],
 'hoogvliet-noord':['hoogvliet-noord','hoogvliet noord'],'hoogvliet-zuid':['hoogvliet-zuid','hoogvliet zuid']}
# CBS-buurten per wijk waar de namen niet vanzelf overeenkomen
BUURT={'oudmathenessewitte-dorp':['Oud Mathenesse','Witte Dorp'],'blijdorpblijdorpsepolder':['Blijdorp','Blijdorpsepolder'],'kralingen-oostkralingse-bos':['Kralingen Oost','Kralingse Bos'],
 'noordkethel-schieveen-zestienhoven':['Noord Kethel','Schieveen','Zestienhoven','Landzicht'],'kralingen-west':['Kralingen West'],'s-gravenland':["'s-Gravenland"],'nieuwe-werkdijkzigt':['Nieuwe Werk','Dijkzigt'],'zuiderpark-en-zuidrand':['Zuiderpark','Charlois Zuidrand'],
 'dorprijnpoort':['Dorp','Rijnpoort'],'groot-ijsselmonde-noord':['Groot IJsselmonde'],'groot-ijsselmonde-zuid':['Groot IJsselmonde'],'kop-van-zuid-entrepot':['Kop van Zuid - Entrepot'],
 'delfshaven-wijk':['Delfshaven'],'feijenoord-wijk':['Feijenoord'],'overschie-wijk':['Overschie'],'pernis-wijk':['Pernis'],'rozenburg-wijk':['Rozenburg'],'cs-kwartier':['Cs Kwartier']}
SOORTNAAM={'Beschikkingen | aanvraag':'aanvraag vergunning','Beschikkingen | afhandeling':'besluit op aanvraag','verkeersbesluit of -mededeling':'verkeersbesluit','ander besluit van algemene strekking':'ander besluit','Overige besluiten van algemene strekking':'ander besluit','Overige overheidsinformatie':'overige informatie','overige overheidsinformatie':'overige informatie'}
# wijkraden (vanaf 2022) en de wijken die ze bestrijken; gebiedscommissies (tot 2022) en de verkiezing tellen niet mee
RAAD={'Dorpsraad Hoek van Holland':['dorprijnpoort','strand-en-duin'],'Wijkraad Hoek van Holland':['dorprijnpoort','strand-en-duin'],
 'Dorpsraad Rozenburg':['rozenburg-wijk'],'Wijkraad Rozenburg':['rozenburg-wijk'],'Wijkcomite Charlois-Pendrecht':['pendrecht'],'Wijkcomite Middelland':['middelland'],
 'Wijkcomite Nesselande':['nesselande'],'Wijkcomite Zevenkamp':['zevenkamp'],'wijkcomité Oud Mathenesse-Witte Dorp':['oudmathenessewitte-dorp'],
 'Wijkraad Afrikaanderwijk':['afrikaanderwijk'],'Wijkraad Agniesebuurt':['agniesebuurt'],'Wijkraad Agniesebuurt-Provenierswijk':['agniesebuurt','provenierswijk'],
 'Wijkraad Provenierswijk':['provenierswijk'],'Wijkraad Bergpolder':['bergpolder'],'Wijkraad Blijdorp':['blijdorpblijdorpsepolder'],'Wijkraad Liskwartier':['liskwartier'],
 'Wijkraad Bergpolder-Blijdorp-Liskwartier':['bergpolder','blijdorpblijdorpsepolder','liskwartier'],'Wijkraad Blijdorp-Bergpolder-Liskwartier':['bergpolder','blijdorpblijdorpsepolder','liskwartier'],
 'Wijkraad Beverwaard':['beverwaard'],'Wijkraad Bloemhof':['bloemhof'],'Wijkraad Bospolder-Spangen-Tussendijken':['bospolder','spangen','tussendijken'],
 'Wijkraad Carnisse-Zuiderpark':['carnisse','zuiderpark-en-zuidrand'],'Wijkraad Carnisse-Zuidplein-Zuiderpark':['carnisse','zuidplein','zuiderpark-en-zuidrand'],
 'Wijkraad Cool-Scheepvaartkwartier-Stadsdriehoek':['cool','stadsdriehoek'],'Wijkraad Crooswijk':['nieuw-crooswijk','oud-crooswijk','rubroek'],
 'Wijkraad Delfshaven-Schiemond':['delfshaven-wijk','schiemond'],'Wijkraad Dijkzigt-Oude Westen':['nieuwe-werkdijkzigt','oude-westen'],
 'Wijkraad Entrepot-Noordereiland':['kop-van-zuid-entrepot','noordereiland'],'Wijkraad Kop van Zuid-Entrepot':['kop-van-zuid-entrepot'],'Wijkraad Noordereiland':['noordereiland'],
 'Wijkraad Feijenoord':['feijenoord-wijk'],'Wijkraad Groot-IJsselmonde en Oud-IJsselmonde':['groot-ijsselmonde-noord','groot-ijsselmonde-zuid','oud-ijsselmonde'],
 'Wijkraad Heijplaat':['heijplaat'],'Wijkraad Het Lage Land, Prinsenland en ’s Gravenland':['het-lage-land','prinsenland','s-gravenland'],
 'Wijkraad Lage Land, Prinsenland en ’s Gravenland':['het-lage-land','prinsenland','s-gravenland'],'Wijkraad Hillegersberg':['hillegersberg-noord','hillegersberg-zuid','molenlaankwartier','terbregge'],
 'Wijkraad Hillesluis':['hillesluis'],'Wijkraad Hoogvliet':['hoogvliet-noord','hoogvliet-zuid'],'Wijkraad Katendrecht-Wilhelminapier':['katendrecht','kop-van-zuid'],
 'Wijkraad Kralingen':['kralingen-west','kralingen-oostkralingse-bos','de-esch','struisenburg'],'Wijkraad Kralingseveer':['kralingseveer'],'Wijkraad Lombardijen':['lombardijen'],
 'Wijkraad Mathenesse':['oudmathenessewitte-dorp'],'Wijkraad Middelland-Nieuwe Westen':['middelland','nieuwe-westen'],'Wijkraad Nesselande':['nesselande'],'Wijkraad Ommoord':['ommoord'],
 'Wijkraad Oosterflank':['oosterflank'],'Wijkraad Oud Charlois-Wielewaal':['oud-charlois','wielewaal'],'Wijkraad Oude Noorden':['oude-noorden'],
 'Wijkraad Overschie':['overschie-wijk','kleinpolder','noordkethel-schieveen-zestienhoven'],'Wijkraad Pendrecht-Zuidwijk':['pendrecht','zuidwijk'],'Wijkraad Pernis':['pernis-wijk'],
 'Wijkraad Schiebroek':['schiebroek'],'Wijkraad Tarwewijk':['tarwewijk'],'Wijkraad Vreewijk':['vreewijk'],'Wijkraad Zevenkamp':['zevenkamp']}
CBSV={'inw':'aantalInwoners','woz':'gemiddeldeWoningwaarde','huur':'percentageHuurwoningen','corp':'percHuurwoningenInBezitWoningcorporaties','ink':'gemiddeldInkomenPerInwoner',
      'laag':'percentageHuishoudensMetLaagInkomen','bijst':'aantalPersonenMetEenAlgBijstandsuitkeringTot','jong':'percentagePersonen0Tot15Jaar','oud':'percentagePersonen65JaarEnOuder',
      'eenp':'percentageEenpersoonshuishoudens','jz':'percentageJongerenMetJeugdzorgInNatura','wmo':'aantalWmoClientenPer1000Inwoners','auto':'personenautosPerHuishouden'}
def lmain():
    W=json.load(open(os.path.join(WERK,'wijk','wijken.json'),encoding='utf8'))
    WP=json.load(open(os.path.join(WERK,'wijk','wijkprofiel.json'),encoding='utf8'))['data']
    wijken=[]
    for g,ws in W.items():
        for s,naam in ws.items():
            zoek=ZOEK.get(s,[naam.replace(' (wijk)','')]) if s in ZOEK else [naam]
            wijken.append({'slug':s,'naam':naam.replace(' (wijk)',''),'gebied':GEBNAAM.get(g,g.capitalize()),'gslug':g,'zoek':zoek,'buurten':BUURT.get(s,[naam])})
    # CBS per jaar
    jaren=['2022','2023','2024','2025']; cbs={}
    for j in jaren:
        p=os.path.join(WERK,'kaart',f'buurten_{j}.json')
        if os.path.exists(p): cbs[j]={f['properties']['buurtnaam']:f for f in json.load(open(p,encoding='utf8'))['features']}
    geo=cbs['2024']
    # kaartgeometrie: zelfde projectie als kaart.py
    import kaart as K
    for w in wijken:
        NB={n(k):k for k in geo}   # buurtnamen zonder verschil in streepjes en hoofdletters
        w['buurten']=[NB[n(b)] for b in w['buurten'] if n(b) in NB] or w['buurten']
        fs=[geo[b] for b in w['buurten'] if b in geo]
        if not fs: print('geen buurt voor',w['naam'],w['buurten'])
        d='';ringen=[]
        for f in fs:
            dd,rr=K.pad(K.geom(f['geometry']),0.5); d+=dd; ringen+=rr
        w['d']=d
        if ringen: cx,cy=K.zw(max(ringen,key=K.opp)); w['lx'],w['ly']=round(cx),round(cy)
        # CBS: som (aantallen) of inwoner-gewogen gemiddelde (percentages, bedragen)
        w['cbs']={}
        for j,B in cbs.items():
            rij=[B[b]['properties'] for b in w['buurten'] if b in B]; out={}
            inw=sum(max(0,r.get('aantalInwoners') or 0) for r in rij)
            for k,v in CBSV.items():
                vals=[(r.get(v),max(0,r.get('aantalInwoners') or 0)) for r in rij if isinstance(r.get(v),(int,float)) and r.get(v)>=0]
                if not vals: continue
                if k in('inw','bijst'): out[k]=sum(a for a,_ in vals)
                else:
                    tw=sum(b for _,b in vals); out[k]=round(sum(a*b for a,b in vals)/tw,1) if tw else round(sum(a for a,_ in vals)/len(vals),1)
            w['cbs'][j]=out
        # Wijkprofiel
        wp=WP.get(w['gslug']+'/'+w['slug'],{})
        w['wp']={j:{k:v.get('index') for k,v in x.items()} for j,x in wp.items()}
        w['wpd']=wp.get('2026') or wp.get('2024')
    # vermeldingen in de raad (spreekbeurten, notulen en ondertiteling)
    TH=[(g[0],t) for g in themes.T for t in g[1]]
    def rx(terms):
        ps=[]
        for t in terms.split('|'):
            t=t.strip(); m=re.match(r'^"(.+)"$',t); core=re.escape(fold(m.group(1) if m else t))
            ps.append(r'(?<![a-z0-9])'+core+r'(?![a-z0-9])' if m else core)
        return re.compile('|'.join(ps))
    ONDERW=[k for k,(g,t) in enumerate(TH) if g!='Wijken en gebieden' and t[0]!='Toezeggingen']
    RT={k:rx(TH[k][1][1]) for k in ONDERW}
    def wrx(zoek):
        ci=[z for z in zoek if z!='Cool']; parts=[(z[3:] if z.startswith('re:') else r'(?<![a-z0-9])'+re.escape(fold(z))+r'(?![a-z0-9])') for z in ci]   # 're:' = eigen patroon
        return re.compile('|'.join(parts)) if parts else None
    for w in wijken:
        w['_rx']=wrx(w['zoek']) if w['zoek'] else None; w['_cool']=w['zoek']==['Cool']
    dz=zstandard.ZstdDecompressor(); words=collections.Counter()
    for w in wijken: w['_n']=collections.Counter(); w['_o']=collections.defaultdict(collections.Counter); w['_frag']={}
    for p in sorted(glob.glob(os.path.join(DOCS,'data','raad','*.zst'))):
        y=os.path.basename(p)[:4]; Y=json.loads(dz.decompress(open(p,'rb').read(),max_output_size=10**9)); s=Y['s']
        for i,t in enumerate(s['t']):
            if s['k'][i] not in(0,4) or not t: continue
            f=fold(t); words[y]+=f.count(' ')+1; raakt=None
            for w in wijken:
                if w['_cool']: h=len(re.findall(r'(?<![A-Za-z])Cool(?![a-z])',t))
                elif w['_rx']: h=len(w['_rx'].findall(f))
                else: continue
                if not h: continue
                w['_n'][y]+=h
                if raakt is None: raakt=[k for k,r in RT.items() if r.search(f)]
                for k in raakt: w['_o'][y][k]+=1
                mt=Y['M'][s['m'][i]]; it=Y['I'][s['i'][i]]
                if h>w['_frag'].get(y,(0,))[0]:
                    m=(re.search(r'(?<![A-Za-z])Cool(?![a-z])',t) if w['_cool'] else w['_rx'].search(f)); a=max(0,m.start()-150); b=min(len(t),m.end()+200)
                    w['_frag'][y]=(h,mt[0],mt[1] or '',(it[1]+' '+it[2]).strip()[:140],('…' if a else '')+re.sub(r'\s+',' ',t[a:b]).strip()+'…',m.start()-a+(1 if a else 0),m.end()-m.start())
    # stukken die de wijk noemen (titel, of minstens 2x in de tekst)
    ST=json.loads(dz.decompress(open(os.path.join(DOCS,'data','ibabs','stukken.zst'),'rb').read(),max_output_size=10**9)); S=ST['soorten']
    for w in wijken:
        w['_st']=[]
    for r in ST['s']:
        ft=fold(r[2]+' '+r[3]); fx=fold(r[6][:6000])
        for w in wijken:
            if w['_cool']: ok=bool(re.search(r'(?<![A-Za-z])Cool(?![a-z])',r[2]))
            elif w['_rx']: ok=bool(w['_rx'].search(ft)) or len(w['_rx'].findall(fx))>=2
            else: continue
            if ok: w['_st'].append(r)
    jr=sorted(words)
    # bron 5: geregistreerde misdrijven (politie via CBS), buurten opgeteld per wijk
    pol={}; p=os.path.join(WERK,'wijk','politie.json')
    if os.path.exists(p):
        P=json.load(open(p,encoding='utf8')); code={f['properties']['buurtnaam']:f['properties']['buurtcode'] for f in geo.values()}
        for w in wijken:
            som=collections.defaultdict(collections.Counter)
            for b in w['buurten']:
                for soort,jr_ in P['buurten'].get(code.get(b,''),{}).items():
                    for j,v in jr_.items():
                        if isinstance(v,(int,float)): som[soort][j]+=v
            pol[w['slug']]={s:dict(sorted(c.items())) for s,c in som.items()}
    # bron 4: bekendmakingen met een locatiepunt -> buurt -> wijk
    bm={w['slug']:{'n':collections.Counter(),'soort':collections.Counter(),'recent':[]} for w in wijken}
    p=os.path.join(WERK,'wijk','bekendmakingen.jsonl')
    if os.path.exists(p):
        ringen=[]
        for w in wijken:
            for b in w['buurten']:
                if b in geo:
                    for poly in K.geom(geo[b]['geometry']):
                        r=poly[0]; ringen.append((w['slug'],r,min(x for x,_ in r),max(x for x,_ in r),min(y for _,y in r),max(y for _,y in r)))
        def binnen(x,y,r):
            c=False
            for i in range(len(r)):
                (x1,y1),(x2,y2)=r[i-1],r[i]
                if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1+1e-12)+x1: c=not c
            return c
        alle=[json.loads(l) for l in open(p,encoding='utf8') if l.strip()]
        for r in sorted(alle,key=lambda r:r['d'],reverse=True):
            if r.get('lon') is None: continue
            x,y=r['lon'],r['lat']
            for slug,ring,a,b_,c,d in ringen:
                if a<=x<=b_ and c<=y<=d and binnen(x,y,ring):
                    B_=bm[slug]; B_['n'][r['d'][:4]]+=1; B_['soort'][SOORTNAAM.get(r['type'],r['type'] or 'overig')]+=1
                    if len(B_['recent'])<10: B_['recent'].append([r['d'],r['titel'][:160],SOORTNAAM.get(r['type'],r['type']),r['url']])
                    break
    # bron 6: vergaderingen van de wijkraden; alleen agendapunt-titels, geen inspreekteksten (namen van bewoners)
    wv={w['slug']:{'n':0,'recent':[],'raad':set()} for w in wijken}
    p=os.path.join(WERK,'wijk','wijkraadvergaderingen.jsonl')
    STANDAARD=re.compile(r'opening|vaststel|mededeling|rondvraag|sluiting|inspre|ingekomen|actielijst|besluitenlijst|notulen|verslag van|agenda|welkom|afsluiting|pauze|wat verder ter tafel|^ter (besluitvorming|bespreking|informatie|kennisname)|:$|\b(dhr|mevr|mw)\b|\b(de heer|mevrouw)\b',re.I)   # ook geen persoonsnamen
    if os.path.exists(p):
        V=[json.loads(l) for l in open(p,encoding='utf8') if l.strip()]
        for w in wijken:
            for v in sorted(V,key=lambda v:v['datum'],reverse=True):
                if v['datum']>STAND: continue   # geplande vergaderingen nog niet
                if w['slug'] not in RAAD.get(re.sub(r'\s*\((in)?formeel\)','',v['raad']).strip(),[]): continue
                wv[w['slug']]['n']+=1; wv[w['slug']]['raad'].add(re.sub(r'\s*\((in)?formeel\)','',v['raad']))
                pt=[i['titel'][:120] for i in v['items'] if i['titel'] and not STANDAARD.search(i['titel'])]
                if pt and len(wv[w['slug']]['recent'])<8: wv[w['slug']]['recent'].append([v['datum'],re.sub(r'\s*\((in)?formeel\)','',v['raad']),pt[:6],'https://wijkraad.rotterdam.nl/Agenda/Index/'+v['id']])
    out=[]
    for w in wijken:
        st=w['_st']; tel=collections.Counter(S[r[0]] for r in st)
        def rij(r): return [r[1],r[2],r[3].split(' (')[0].split(' · ')[0],r[5],r[7] if r[7].startswith('http') else 'https://gemeenteraad.rotterdam.nl/Reports/Item/'+r[7],r[8]]
        o=collections.Counter(); [o.update(v) for v in w['_o'].values()]
        out.append({'slug':w['slug'],'naam':w['naam'],'gebied':w['gebied'],'zoek':w['zoek'],'d':w['d'],'lx':w.get('lx'),'ly':w.get('ly'),
            'cbs':w['cbs'],'wp':w['wp'],'wpd':w['wpd'],
            'n':{y:w['_n'][y] for y in jr},'per':{y:round(w['_n'][y]/words[y]*1e5,2) for y in jr},
            'onderwerpen':[[TH[k][1][0],c] for k,c in o.most_common(6)],
            'frag':{y:list(v[1:]) for y,v in w['_frag'].items()},
            'stukken':{k:tel[k] for k in tel},
            'moties':[rij(r) for r in st if S[r[0]]=='Motie'][:8],'toez':[rij(r) for r in st if S[r[0]]=='Toezegging'][:6],
            'sv':[rij(r) for r in st if S[r[0]]=='Schriftelijke vragen'][:6],
            'wijkraad':[rij(r) for r in st if S[r[0]].startswith(('Wijk','Ongevraagd','Collegereactie'))][:8],
            'politie':pol.get(w['slug'],{}),
            'bekend':{'n':dict(sorted(bm[w['slug']]['n'].items())),'soort':bm[w['slug']]['soort'].most_common(8),'recent':bm[w['slug']]['recent']},
            'wrv':{'n':wv[w['slug']]['n'],'raad':sorted(wv[w['slug']]['raad']),'recent':wv[w['slug']]['recent']}})
    json.dump({'jaren':jr,'bron_wp':'Cijfers: gemeente Rotterdam; OBI, Wijkprofiel 2014-2026','bron_cbs':'CBS Kerncijfers wijken en buurten 2022-2025, via PDOK','wijken':out},
              open(os.path.join(DOCS,'wijken.json'),'w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
    print(len(out),'wijken',os.path.getsize(os.path.join(DOCS,'wijken.json'))//1000,'kB')
    for w in sorted(out,key=lambda w:-sum(w['n'].values()))[:12]: print(w['naam'],sum(w['n'].values()),w['stukken'].get('Motie',0),w['cbs'].get('2024',{}).get('inw'),w['wp'].get('2026'))
if __name__=='__main__': lmain()
