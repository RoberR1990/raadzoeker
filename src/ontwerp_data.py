# Data voor de ontwerpschermen -> docs/ontwerp/{dossiers,lab}.json
# dossiers.json: per thema (41, uit themes.py) trend, partijen, collegeleden, AI-samenvatting, moties en toezeggingen
#   (open en afgedaan, met letterlijke kern uit de motietekst), schriftelijke vragen, rekenkamer, debatten met fragment;
#   voor de 14 gebieden ook onderwerpen per jaar, wijkraadstukken en inwoners.
# lab.json: samenwerking tussen fracties, slagingskans moties, doorlooptijd toezeggingen, Wrapped per jaar.
import json,os,re,collections,unicodedata,zstandard,glob,statistics,datetime
from paden import DOCS,DATA,STAND,WERK
import themes,onderwerpen
def fold(s): return ''.join(c for c in unicodedata.normalize('NFD',s.lower()) if unicodedata.category(c)!='Mn').replace('’',"'").replace('‘',"'")
def rx(terms):
    ps=[]
    for t in terms.split('|'):
        t=t.strip(); m=re.match(r'^"(.+)"$',t); core=re.escape(fold(m.group(1) if m else t))
        ps.append(r'(?<![a-z0-9])'+core+r'(?![a-z0-9])' if m else core)
    return re.compile('|'.join(ps))
dz=zstandard.ZstdDecompressor()
def zload(p): return json.loads(dz.decompress(open(p,'rb').read(),max_output_size=10**9))
def iso(d):
    m=re.search(r'(\d\d)-(\d\d)-(\d{4})',d or ''); return f'{m.group(3)}-{m.group(2)}-{m.group(1)}' if m else ''
def kort(s,n):
    s=re.sub(r'^o\s+','',s.strip(' ;,.:•-–')); return s if len(s)<=n else s[:n].rsplit(' ',1)[0]+'…'
BUL=r'(?:•|·|▪|-|–|\d{1,2}[.)]|(?<=\s)o(?=\s))'   # 'o' = opsommingsteken na ocr
def motiekern(t):
    """Letterlijke kern uit een motietekst: eerste constatering en eerste verzoek (geen AI)."""
    t=re.sub(r'\s+',' ',t or '')
    out={}
    m=re.search(r'constaterende,?\s*(?:dat)?\s*:?\s*'+BUL+r'?\s*(.{15,600}?)(?=\s*(?:;|\. |'+BUL+r'\s|overwegende|verzoekt|$))',t,re.I)
    if m: out['c']=kort(m.group(1),220)
    m=re.search(r'(?:verzoekt|draagt)\s+(?:het\s+)?(?:college|de burgemeester)[^:•]{0,40}?:?\s*(?:om\s*:?)?\s*'+BUL+r'?\s*(.{15,600}?)(?=\s*(?:;|\. |'+BUL+r'\s|en gaat over|$))',t,re.I)
    if m: out['v']=kort(m.group(1),260)
    return out
def main():
    meta=json.load(open(f'{DOCS}/data/raad/meta.json',encoding='utf8')); I=meta['ins']; SPK=meta['spk']; PAR=meta['par']
    TH=[(g[0],t) for g in themes.T for t in g[1]]; R=[rx(t[1]) for _,t in TH]
    GEB=[k for k,(g,_) in enumerate(TH) if g=='Wijken en gebieden' and TH[k][1][0]!='Nationaal Programma Rotterdam Zuid']
    ONDERW=[k for k,(g,t) in enumerate(TH) if g!='Wijken en gebieden' and t[0]!='Toezeggingen']
    OND=onderwerpen.actief(); NT=len(TH); R2=R+[onderwerpen.rx(pp) for _,pp in OND]   # concrete onderwerpen na de thema's
    tsum={d['id']:d for f in glob.glob(f'{DATA}/tsum/out_*.json') for d in json.load(open(f,encoding='utf8'))}
    kaart=json.load(open(f'{DOCS}/ontwerp/kaart.json',encoding='utf8')); INW={g['naam']:g['inw'] for g in kaart['gebieden']}
    ST=zload(f'{DOCS}/data/ibabs/stukken.zst'); S=ST['soorten']
    # stemuitslag uit de notulen per motie (bb-nummer), via de koppeling notulen <-> iBabs
    STEM={}
    for key,bb in json.load(open(f'{DOCS}/data/ibabs/moties.json')).items():
        y,k=key.split(':'); STEM.setdefault(y,{})[int(k)]=bb
    for y,kk in list(STEM.items()):
        Y=zload(f'{DOCS}/data/raad/{y}.zst')
        for k,bb in kk.items():
            m=Y['mo'][k]; STEM[bb]=[m[4],m[5],m[6],m[7],m[8]]   # aangenomen, voor, tegen, zijde (v/t), genoemde fracties
        del STEM[y]
    per=collections.defaultdict(list)
    for r in ST['s']:
        ft=fold(r[2]); fx=fold(r[6][:6000])
        for k,rr in enumerate(R2):
            if rr.search(ft) or len(rr.findall(fx))>=3: per[k].append(r)
    # debatten (raad): treffers per vergadering/agendapunt per thema, beste fragment; onderwerpen per gebied per jaar
    deb=collections.defaultdict(collections.Counter); best={}; spk=collections.defaultdict(collections.Counter)
    wt=collections.defaultdict(lambda:collections.defaultdict(collections.Counter))
    co=collections.defaultdict(collections.Counter); segn=collections.Counter(); NSEG=[0]   # samen genoemd in een spreekbeurt
    WY=collections.Counter(); WP=collections.Counter(); KY=collections.defaultdict(collections.Counter); KP=collections.defaultdict(collections.Counter)   # woorden en treffers per jaar/fractie (voor onderwerpen)
    for p in sorted(glob.glob(f'{DOCS}/data/raad/*.zst')):
        Y=zload(p); s=Y['s']; y=os.path.basename(p)[:4]
        for i,t in enumerate(s['t']):
            if s['k'][i] not in(0,4) or not t: continue
            f=fold(t); mt=Y['M'][s['m'][i]]; it=Y['I'][s['i'][i]]
            key=(mt[0],mt[1] or '',(it[1]+' '+it[2]).strip())
            raak={}
            for k,rr in enumerate(R2):
                h=rr.findall(f)
                if h: raak[k]=len(h)
            nw=len(t.split()); WY[y]+=nw
            if s['pa'][i]>=0: WP[PAR[s['pa'][i]]]+=nw
            for k,c in raak.items():
                if k>=NT:
                    KY[k][y]+=c
                    if s['pa'][i]>=0: KP[k][PAR[s['pa'][i]]]+=c
            for k,c in raak.items():
                deb[k][key]+=c
                if s['sp'][i]>=0: spk[(k,key)][SPK[s['sp'][i]][0]+(' ('+PAR[s['pa'][i]]+')' if s['pa'][i]>=0 else '')]+=c
                if c>best.get((k,key),(0,))[0]:
                    m=R2[k].search(f); a=max(0,m.start()-140); b=min(len(t),m.end()+200)
                    best[(k,key)]=(c,('…' if a else '')+re.sub(r'\s+',' ',t[a:b]).strip()+('…' if b<len(t) else ''),m.start()-a+(1 if a else 0),m.end()-m.start(),s['k'][i])
            NSEG[0]+=1
            for k in raak:
                segn[k]+=1
                for j in raak:
                    if j!=k: co[k][j]+=1
            for g in GEB:
                if g in raak:
                    for k in raak:
                        if k in ONDERW: wt[g][y][k]+=1
    def rij(r):
        x=[r[1],r[2],r[3].split(' (')[0].split(' · ')[0],r[5],r[7] if r[7].startswith('http') else 'https://gemeenteraad.rotterdam.nl/Reports/Item/'+r[7],r[8]]
        if S[r[0]] in('Motie','Amendement','Initiatiefvoorstel'):
            c=motiekern(r[6])
            if r[8] in STEM: c['s']=STEM[r[8]]
            x.append(c)
        elif S[r[0]]=='Toezegging': x.append({'o':kort(re.sub(r'\s+',' ',r[6].split('\nStand van zaken')[0]),260)} if r[6] else {})
        else: x.append({})
        return x
    jaren=I['years']; out=[]
    def afdatum(r): return iso((re.search(r'afgedaan ([\d-]+)',r[5]) or [None,''])[1])
    def dagen(a,b): return (datetime.date.fromisoformat(b)-datetime.date.fromisoformat(a)).days
    alle_af=[dagen(r[1],afdatum(r)) for r in ST['s'] if S[r[0]]=='Motie' and r[4]==5 and afdatum(r)]
    STAD_MED=round(statistics.median(alle_af)) if alle_af else None
    def verdieping(k,mot,toez,rs):
        # 1 tijdlijn
        pd=collections.Counter()
        for (dt,a,ti),c in deb[k].items(): pd[dt]+=c
        tl={'deb':sorted([d_,c] for d_,c in pd.items() if c>=2),
            'mot':[[r[1],{1:'a',4:'a',5:'a',2:'v',3:'i'}.get(r[4],'o')] for r in mot],
            'toez':[r[1] for r in toez],'rk':[[r[1],r[2]] for r in rs if S[r[0]]=='Rekenkamerrapport']}
        # 2 afdoening per jaar en doorlooptijd
        aan=[r for r in mot if r[4] in(1,4,5)]
        pj={y:[sum(1 for r in aan if r[1][:4]==y),sum(1 for r in aan if r[1][:4]==y and r[4]==5)] for y in jaren}
        dl=[dagen(r[1],afdatum(r)) for r in aan if r[4]==5 and afdatum(r)]
        # 3 wie zit er aan tafel
        ind=collections.Counter(r[3].split(' (')[0].strip() for r in mot if r[3]); ok=collections.Counter(r[3].split(' (')[0].strip() for r in aan if r[3])
        tz=collections.Counter(re.sub(r'\s*\(.*','',r[3].split(' · ')[0]).strip() for r in toez if r[3]); tzo=collections.Counter(re.sub(r'\s*\(.*','',r[3].split(' · ')[0]).strip() for r in toez if r[3] and r[4]==4)
        # 4 botsingen: nipte stemmingen
        nip=[r for r in mot if r[8] in STEM and STEM[r[8]][1]>=0]
        nip.sort(key=lambda r:(abs(STEM[r[8]][1]-STEM[r[8]][2]),-int(r[1][:4]+r[1][5:7]+r[1][8:])))
        # 5 verwante onderwerpen (lift: hoeveel vaker samen dan toeval), 6 wijken
        n=max(1,segn[k]); N=max(1,NSEG[0])
        ver=[[TH[j][1][0],round(100*c/n),round((c/n)/(segn[j]/N),1)] for j,c in co[k].items() if j in ONDERW and c>=15]
        ver=sorted(ver,key=lambda x:-x[2])[:6]
        wijk={TH[g][1][0]:round(100*co[k][g]/n,1) for g in GEB if g!=k}
        if k>=NT: ver=sorted([[TH[j][1][0],round(100*c/n),round((c/n)/(segn[j]/N),1)] for j,c in co[k].items() if j<NT and j in ONDERW and c>=5],key=lambda x:-x[2])[:6]
        return {'tl':tl,'pj':pj,'dl':round(statistics.median(dl)) if dl else None,'dln':len(dl),'stad_dl':STAD_MED,
                'ind':[[p,c,ok[p]] for p,c in ind.most_common(8)],'tz':[[w,c,tzo[w]] for w,c in tz.most_common(5)],
                'nip':[rij(r) for r in nip[:6]],'ver':ver,'wijk':wijk}
    def dossier(k,groep,t,trend,trendn,partijen,college,ts):
        rs=per[k]
        mot=[r for r in rs if S[r[0]]=='Motie']; aan=[r for r in mot if r[4] in(1,4,5)]
        toez=[r for r in rs if S[r[0]]=='Toezegging']
        def laat(r): d=iso((re.search(r'verwacht ([\d-]+)',r[5]) or [None,''])[1]); return bool(d) and d<STAND
        top=sorted(deb[k].items(),key=lambda x:(-(x[0][0]>='2025'),-x[1]))[:6]
        d={'id':k,'naam':t[0],'groep':groep,'termen':t[1],'sub':[s[0] for s in t[2]],
           'trend':trend,'trendn':trendn,'jaren':jaren,'partijen':partijen,'college':college,'tsum':ts,
           'moties':{'aangenomen':len(aan),'open':sum(1 for r in mot if r[4]==4),'afgedaan':sum(1 for r in mot if r[4]==5),
                     'verworpen':sum(1 for r in mot if r[4]==2),'te_laat':sum(1 for r in mot if r[4]==4 and laat(r)),
                     'lijst':[rij(r) for r in mot if r[4]==4][:12],'af':[rij(r) for r in mot if r[4]==5][:12],
                     'perjaar':dict(collections.Counter(r[1][:4] for r in aan))},
           'toez':{'open':sum(1 for r in toez if r[4]==4),'te_laat':sum(1 for r in toez if r[4]==4 and laat(r)),'afgedaan':sum(1 for r in toez if r[4]==5),
                   'lijst':[rij(r) for r in toez if r[4]==4][:12],'af':[rij(r) for r in toez if r[4]==5][:12]},
           'sv':{'n':sum(1 for r in rs if S[r[0]]=='Schriftelijke vragen'),'lijst':[rij(r) for r in rs if S[r[0]]=='Schriftelijke vragen'][:6]},
           'rekenkamer':{'n':sum(1 for r in rs if S[r[0]]=='Rekenkamerrapport'),'lijst':[rij(r) for r in rs if S[r[0]]=='Rekenkamerrapport'][:5]},
           'debatten':[[dt,a,ti[:160],c,best[(k,(dt,a,ti))][1],best[(k,(dt,a,ti))][2],best[(k,(dt,a,ti))][3],
                        [n for n,_ in spk[(k,(dt,a,ti))].most_common(3)],best[(k,(dt,a,ti))][4]] for (dt,a,ti),c in top]}
        d['verdieping']=verdieping(k,mot,toez,rs)
        if k in GEB:
            d['inw']=INW.get(t[0],0)
            d['onderwerpen']={y:[[TH[j][1][0],c] for j,c in wt[k][y].most_common(6)] for y in jaren}
            alles=collections.Counter(); [alles.update(v) for v in wt[k].values()]
            d['onderwerpen']['alle']=[[TH[j][1][0],c] for j,c in alles.most_common(8)]
            d['wijkraad']=[rij(r) for r in ST['s'] if (S[r[0]].startswith(('Wijk','Ongevraagd','Collegereactie'))) and R[k].search(fold(r[3]+' '+r[2]))][:15]
        return d
    for k,(groep,t) in enumerate(TH):
        out.append(dossier(k,groep,t,I['ty'][k],I['tyn'][k],sorted(zip(I['parties'],I['tp'][k]),key=lambda x:-x[1]),
                           sorted([(c,v) for c,v in zip(I['coll'],I['tw'][k])],key=lambda x:-x[1])[:5],tsum.get(k)))
    ond=[]
    for j,(naam,pp) in enumerate(OND):
        k=NT+j; trn=[KY[k][y] for y in jaren]; tr=[round(KY[k][y]/max(1,WY[y])*1e5,1) for y in jaren]
        pa=sorted([(p,round(c/max(1,WP[p])*1e5,1)) for p,c in KP[k].items() if WP[p]>20000],key=lambda x:-x[1])
        d=dossier(k,onderwerpen.THEMA[naam],(naam,onderwerpen.termen(pp),[]),tr,trn,pa,[],None); d['soort']='onderwerp'
        d['verdieping']['ver']=[v for v in d['verdieping']['ver'] if v[0]!=d['groep']]   # eigen thema is geen verband
        d['ai']=os.path.exists(f'{DOCS}/ontwerp/samenvattingen/'+re.sub(r'[^a-z0-9]+','-',fold(naam)).strip('-')+'.json')
        ond.append(d)
    # stadsbreed: onderwerpen per jaar (per 100.000 woorden)
    stad={y:sorted([[TH[k][1][0],I['ty'][k][j]] for k in ONDERW],key=lambda x:-x[1])[:6] for j,y in enumerate(jaren)}
    json.dump({'stand':STAND,'dossiers':out,'stad':stad},open(f'{DOCS}/ontwerp/dossiers.json','w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
    json.dump({'stand':STAND,'onderwerpen':ond},open(f'{DOCS}/ontwerp/onderwerpen.json','w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))   # concrete onderwerpen, apart geladen
    print('dossiers',len(out),os.path.getsize(f'{DOCS}/ontwerp/dossiers.json')//1000,'kB')
    lab(ST,S,I,TH,ONDERW,GEB)
    start(ST,S,I,meta,out,stad)
def start(ST,S,I,meta,dossiers,stad):
    mot=[r for r in ST['s'] if S[r[0]]=='Motie']
    laatst=max(r[1] for r in mot if r[4] in(1,4,5))
    recent=[[r[1],r[2],r[3].split(' (')[0],r[5],'https://gemeenteraad.rotterdam.nl/Reports/Item/'+r[7],motiekern(r[6])] for r in mot if r[1]==laatst and r[4] in(1,4,5)]
    def laat(r): d=iso((re.search(r'verwacht ([\d-]+)',r[5]) or [None,''])[1]); return bool(d) and d<STAND
    toez=[r for r in ST['s'] if S[r[0]]=='Toezegging' and r[4]==4]; mo=[r for r in mot if r[4]==4]
    out={'stand':STAND,'laatst':laatst,'recent':recent,'aantal_aangenomen':len(recent),
         'toez_open':len(toez),'toez_laat':sum(1 for r in toez if laat(r)),'mot_open':len(mo),'mot_laat':sum(1 for r in mo if laat(r)),
         'soorten':S,'rise':[[w[0],w[1],w[2],w[3]] for w in I['rise'][:8]],'jaren':I['years'],'stad':stad,
         # klein genoeg voor de startpagina: zoeklijst + wolk (aandacht dit en vorig jaar) en de gebieden voor de kaart
         'ond':[[d['naam'],d['groep'],d['sub'],d['termen'],d['trend'][-1],d['trend'][-2],d['trendn'][-1]] for d in dossiers if d['naam']!='Toezeggingen'],
         'geb':{d['naam']:{'trend':d['trend'],'trendn':d['trendn'],'onderwerpen':d['onderwerpen']} for d in dossiers if 'inw' in d}}
    json.dump(out,open(f'{DOCS}/ontwerp/start.json','w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
    print('start',len(recent),'besluiten op',laatst,out['toez_open'],out['toez_laat'],out['mot_open'],out['mot_laat'])
def lab(ST,S,I,TH,ONDERW,GEB):
    L=json.load(open(os.path.join(WERK,'ibabs','lijsten.json'),encoding='utf8'))
    P0,P1='2022-03-30','2026-03-25'   # raadsperiode 2022-2026: vaste set fracties
    def norm(p): return {'GroenLinks-PvdA':'GroenLinks-PvdA'}.get(p.strip(),p.strip())
    pair=collections.Counter(); ind=collections.Counter(); aang=collections.Counter()
    for r in L['moties']:
        d=iso(r['registrationdate'])
        if not(P0<=d<=P1) or not r.get('partij'): continue
        ps={norm(r['partij'])}|{norm(x) for x in re.split(r'[;,\n]',r.get('medeindiendepartijen') or '') if x.strip()}
        for p in ps:
            ind[p]+=1
            if (r.get('uitslag') or '').lower().startswith('aangenomen'): aang[p]+=1
        ps=sorted(ps)
        for i in range(len(ps)):
            for j in range(i+1,len(ps)): pair[(ps[i],ps[j])]+=1
    partijen=[p for p,n in ind.most_common() if n>=20]
    # doorlooptijd toezeggingen per collegelid (raadsperiode 2022-2026)
    dl=collections.defaultdict(list); ov=collections.Counter(); tot=collections.Counter()
    p=os.path.join(WERK,'ibabs','items_toezeggingen.jsonl')
    for l in open(p,encoding='utf8'):
        x=json.loads(l); r=x['lijst']; D=x['detail']; d0=iso(r['registrationdate']); d1=iso(D.get('Datum afgedaan') or ''); dv=iso(D.get('Verwachte datum afdoening') or '')
        wie=re.sub(r'\s*\(.*','',(r.get('portefeuillehouder') or '').strip())
        if not(P0<=d0<=P1) or not wie: continue
        tot[wie]+=1
        if d1:
            dl[wie].append((datetime.date.fromisoformat(d1)-datetime.date.fromisoformat(d0)).days)
            if dv and d1>dv: ov[wie]+=1
    # open toezeggingen per collegelid nu (alle jaren), en hoeveel over de termijn
    ot=collections.Counter(); otl=collections.Counter()
    for r in ST['s']:
        if S[r[0]]=='Toezegging' and r[4]==4:
            w=re.sub(r'\s*\(.*','',r[3].split(' · ')[0]).strip(); ot[w]+=1
            dv=iso((re.search(r'verwacht ([\d-]+)',r[5]) or [None,''])[1])
            if dv and dv<STAND: otl[w]+=1
    openper=[[w,n,otl[w]] for w,n in ot.most_common() if n>=5]
    # schriftelijke vragen per fractie per jaar
    svj=collections.defaultdict(collections.Counter)
    for r in L['schriftelijke_vragen']:
        d=iso(r['registrationdate'])
        if d>='2018' and r.get('partij'): svj[norm(r['partij'].split('\n')[0])][d[:4]]+=1
    svtop=[p for p,_ in sorted(svj.items(),key=lambda x:-sum(x[1].values()))[:12]]
    door=sorted([[w,round(statistics.median(v)),len(v),round(100*ov[w]/len(v))] for w,v in dl.items() if len(v)>=25],key=lambda x:x[1])
    # Wrapped per jaar
    mot=[r for r in ST['s'] if S[r[0]]=='Motie']; wr={}
    gebnamen=[TH[k][1][0] for k in GEB]
    for j,y in enumerate(I['years']):
        my=[r for r in mot if r[1][:4]==y]
        g=sorted(GEB,key=lambda k:-I['ty'][k][j])
        stijger=None
        if j:
            c=[(I['ty'][k][j]/max(I['ty'][k][j-1],0.5),k) for k in ONDERW if I['tyn'][k][j]>=60]
            if c: f,k=max(c); stijger=[TH[k][1][0],round(f,1)]
        pc=collections.Counter(r[3].split(' (')[0] for r in my)
        wr[y]={'gebied':[TH[g[0]][1][0],TH[g[1]][1][0],TH[g[2]][1][0]],'moties':len(my),'aangenomen':sum(1 for r in my if r[4] in(1,4,5)),
               'toppartij':pc.most_common(3),'stijger':stijger}
    lab={'periode':[P0,P1],'partijen':partijen,'ind':{p:ind[p] for p in partijen},'aang':{p:aang[p] for p in partijen},
         'pair':[[a,b,n] for (a,b),n in pair.items() if a in partijen and b in partijen],'door':door,'wrapped':wr,'openper':openper,
         'sv':{p:dict(svj[p]) for p in svtop},
         'thema':[[TH[k][1][0],TH[k][0]] for k in range(len(TH))],'ty':I['ty'],'jaren':I['years'],'tp':I['tp'],'tpart':I['parties']}
    json.dump(lab,open(f'{DOCS}/ontwerp/lab.json','w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
    print('lab',len(partijen),'partijen',len(lab['pair']),'paren',len(door),'collegeleden',os.path.getsize(f'{DOCS}/ontwerp/lab.json')//1000,'kB')
if __name__=='__main__': main()
