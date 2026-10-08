# Verkenner: kennisgraaf van alles wat de raad zei en schreef (proef 5-10-2026).
#   python src/verkenner.py  -> docs/verkenner.json (graaf + filters) en verkenner-vb.json (voorbeeldfragmenten)
# Eenheden: debatbeurten (spreker x agendapunt) en officiële stukken. Knopen: de onderwerpen (zoekpatronen uit onderwerpen.py),
# de gebieden en wijken, en ca. 2.400 kenmerkende begrippen. Kenmerkend = komt in genoeg eenheden voor en is ongelijk verdeeld
# over de domeinen of gebieden (algemene woorden zoals 'belangrijk' vallen zo vanzelf af). Namen van personen gaan eruit.
# Verband = twee knopen in hetzelfde tekstvenster (ca. 400 tekens); sterkte = genormaliseerde PMI. Per knoop de sterkste verbanden.
# Indeling vooraf berekend (krachtmodel, numpy). Geen AI.
import json,os,re,glob,math,collections,unicodedata
import numpy as np
from paden import DOCS,STAND,WERK
from ontwerp_data import zload
import teksten as T, onderwerpen as OW, gebieden as GB
from dossier_data import slug as SLUG
JAREN=[str(j) for j in range(2018,2027)]; NV=3000; VENSTER=400; TOP=7
TITEL={'mevrouw','mevr','heer','meneer','dhr','collega','wethouder','burgemeester','lid','raadslid','voorzitter','commissielid','wethouders','dames','mr','drs','ir','dr'}
EXTRA_STOP={'rotterdam','rotterdamse','rotterdammers','rotterdammer','gemeente','gemeentelijke','college','raad','motie','moties','wethouder','voorzitter','commissie','https','www','pagina','bijlage','januari','februari','maart','april','juni','juli','augustus','september','oktober','november','december','maandag','dinsdag','woensdag','donderdag','vrijdag','zaterdag','zondag',
 # vergader- en formulierjargon
 'besluitenlijst','rondvraag','actielijst','actiepuntenlijst','vergaderoverzicht','adviesformulier','beoordelingsformulier','aanvraagformulier','dossiernummer',
 'registratienr','volgnr','zaaknummer','antwoordnummer','specificeer','afwijzen','motivering','invulformat','subtitel','uitbetaaladres','handtekeningenblad',
 'toetsingsvragen','startfase','vaststellingsfase','beroepsfase','uitvoeringsdatum','bibliothe','nieuwe','groot','rijden','gebiedsverslag','oplegnotitie',
 # eed en belofte bij installatie
 'getrouw','geschenk','gift','middellijk','onmiddellijk','zweer','beloof','verklaar','almachtig','helpe','gestand','grondwet','waarlijk',
 'apel'}   # losse namen die door de filters glipten
# Een woord dat bijna altijd met een hoofdletter staat, is meestal een naam. Dat mag alleen blijven als het een plek, straat,
# afkorting of herkenbaar beleidswoord is; namen van personen (insprekers, bewoners, ambtenaren) gaan zo de graaf niet in.
ACHTER=re.compile(r'(straat|weg|plein|laan|singel|kade|dijk|park|hof|dreef|baan|haven|brug|tunnel|buurt|kwartier|polder|plaat|waard|gracht|plas|bos|tuin|kerk|museum|markt|hal|eiland|boulevard|wal|steeg|centrum|oord|plan|wet|visie|nota|fonds|programma|aanpak|monitor|akkoord|verordening|festival|regeling|strategie|agenda|dag|feest|loket|bank|bedrijf|lijn|net|dienst|team|punt|school|zone|route|autoriteit|alliantie|pact|kader|reglement|scan|bureau|platform|campus|theater|bios)$')
PLAATS={'feyenoord','kuip','botlek','europoort','maasvlakte','ahoy','erasmus','boijmans','kunsthal','schiphol','delft','schiedam','vlaardingen','capelle','barendrecht','ridderkerk','dordrecht','amsterdam','utrecht','haag','brabant','zeeland','nederland','europa','oekraine','israel','palestina','gaza','suriname','marokko','turkije','antillen','curacao','bonaire','pijnacker','nootdorp','maassluis','moerdijk','voorne','lansingerland'}

def eenheden():
    """per eenheid: (bron 'd'/'s', id, jaar, domein-index of -1, gebieden-bitmasker, fractie-index of -1, tekst, meta)"""
    dm=zload(os.path.join(DOCS,'data','debat','meta.zst')); B=dm['blok']
    for p in sorted(glob.glob(os.path.join(DOCS,'data','debat','b','*.zst'))):
        blk=zload(p); b0=int(os.path.basename(p)[:4])*B
        for j,segs in enumerate(blk):
            U=dm['u'][b0+j]; A=dm['ap'][U[0]]; V=dm['verg'][A[0]]
            wie=dm['spk'][U[1]] if U[1]>=0 else ''
            yield 'd',b0+j,V[0][:4],A[3],A[4],U[2],segs,(V,A,wie,U)
    tm=zload(os.path.join(DOCS,'data','tekst','meta.zst')); lab=zload(os.path.join(DOCS,'data','tekst','labels.zst')); BT=tm['blok']
    for p in sorted(glob.glob(os.path.join(DOCS,'data','tekst','b','*.zst'))):
        blk=zload(p); b0=int(os.path.basename(p).split('.')[0])*BT
        for j,t in enumerate(blk):
            i=b0+j
            if i>=len(tm['d']) or not t: continue
            r=tm['d'][i]; yield 's',i,r[1][:4],lab['d'][i],lab['g'][i],-1,r[2]+'. '+t,(r,)

def fa2(M,ei,ej,ew,iters=700,kr=12.0,kg=1.0,seed=7):
    """ForceAtlas2 (Jacomy e.a. 2014), dichte numpy-versie: afstoting ~ massa_i*massa_j/d, aantrekking ~ gewicht*log(1+d) (linlog,
    geeft duidelijke clusters), hubs afgeremd (aantrekking gedeeld door massa), zwaartekracht naar het midden, adaptieve stapgrootte."""
    rng=np.random.default_rng(seed); X=rng.normal(0,1,(M,2))*100
    m=1.0+np.bincount(np.r_[ei,ej],minlength=M); Fv=np.zeros((M,2)); speed=1.0
    for it in range(iters):
        D=X[:,None,:]-X[None,:,:]; d2=(D**2).sum(-1); np.fill_diagonal(d2,1); d2=np.maximum(d2,1e-2)
        F=kr*((m[:,None]*m[None,:]/d2)[...,None]*D).sum(1)
        dv=X[ei]-X[ej]; att=(ew/ew.mean())[:,None]*dv
        np.add.at(F,ei,-att); np.add.at(F,ej,att)
        r=np.sqrt((X**2).sum(1))+1e-9; F-=(kg*m/r+0.0015*m)[:,None]*X
        sw=np.sqrt(((F-Fv)**2).sum(1)); tr=np.sqrt(((F+Fv)**2).sum(1))/2
        gs=(m*sw).sum(); gt=(m*tr).sum(); ns=gt/max(gs,1e-9)
        speed=min(ns,1.5*speed) if it else ns
        fac=speed/(1+np.sqrt(speed*sw)); L=np.sqrt((F**2).sum(1))+1e-9; fac=np.minimum(fac,10/L)
        X+=F*fac[:,None]; Fv=F
        if it%175==0: print('indeling',it,round(float(speed),3))
    # blaadjes (1-2 verbanden) worden door de dichte kern ver weggeduwd: zet ze vlak bij hun buren
    buur=collections.defaultdict(list)
    for a,b in zip(ei,ej): buur[a].append(b); buur[b].append(a)
    for _ in range(2):
        for i in range(M):
            if len(buur[i])<=2:
                c=X[buur[i]].mean(0); h=rng.uniform(0,2*np.pi); X[i]=c+np.array([np.cos(h),np.sin(h)])*rng.uniform(15,45)*(1+np.sqrt(speed))
    X-=np.median(X,0); sc=np.percentile(np.abs(X),99.5); return np.clip(X/sc*1000,-1300,1300)

def grootste(d):
    """alleen de grootste samenhangende groep houden: losse eilandjes van een paar woorden trekken de kaart uit elkaar"""
    n=len(d['knopen']); ouder=list(range(n))
    def wortel(x):
        while ouder[x]!=x: ouder[x]=ouder[ouder[x]]; x=ouder[x]
        return x
    for a,b,w,c in d['e']: ouder[wortel(a)]=wortel(b)
    cnt=collections.Counter(wortel(i) for i in range(n)); top=cnt.most_common(1)[0][0]
    houd=[i for i in range(n) if wortel(i)==top]; nw={o:i for i,o in enumerate(houd)}
    d['knopen']=[d['knopen'][i] for i in houd]
    for k in ('jg','jd','jf'): d[k]=[d[k][i] for i in houd]
    d['e']=[[nw[a],nw[b],w,c] for a,b,w,c in d['e'] if a in nw and b in nw]
    return d

def herindeel():
    """alleen de indeling opnieuw, op de bestaande verkenner.json"""
    p=os.path.join(DOCS,'verkenner.json'); d=json.load(open(p,encoding='utf8'))
    d=grootste(d)
    e=np.array([[a,b,w] for a,b,w,c in d['e']],float)
    X=fa2(len(d['knopen']),e[:,0].astype(int),e[:,1].astype(int),e[:,2])
    for k,(x,y) in zip(d['knopen'],X.tolist()): k['x']=round(x,1); k['y']=round(y,1)
    json.dump(d,open(p,'w',encoding='utf8'),ensure_ascii=False,separators=(',',':')); print('indeling klaar')

MAILURL=re.compile(r'\S+@\S+|https?://\S+|www\.\S+')
def tekst(x): return MAILURL.sub(' ',' '.join(s for _,s in x) if isinstance(x,list) else x)   # e-mailadressen en links bevatten vaak namen

def main():
    dm=zload(os.path.join(DOCS,'data','debat','meta.zst')); NDOM=len(dm['dom']); GL=dm['geb']; PAR=dm['par']
    pers=set()
    for n in dm['spk']:
        for w in re.findall(r'[^\W\d_]+',n): pers.add(T.fold(w))
    pers|={T.fold(x) for x in GB.achternamen()}
    wk=json.load(open(os.path.join(DOCS,'wijken.json'),encoding='utf8'))['wijken']
    GENERIEK={T.stam(x) for x in ('nieuwe','nieuw','west','westen','oost','oosten','noord','zuid','groot','grote','oude','holland','hoek','centrum','stad','dorp','park','haven','polder','oever','kade','plein')}
    plek={T.stam(T.fold(w)) for g in GL+[x['naam'] for x in wk] for w in re.findall(r'[^\W\d_]+',g) if len(w)>=5}-GENERIEK
    ST=json.load(open(os.path.join(WERK,'gebied','straten.json'),encoding='utf8'))
    straat={T.stam(T.fold(n)) for n in ST if ' ' not in n and ACHTER.search(T.fold(n))}|{T.stam(T.fold(w)) for v in ST.values() for w in re.findall(r'[^\W\d_]+',v.get('woonplaats','')) if len(w)>=5}
    straat|={T.stam(x) for x in PLAATS}
    cache={}; STOPK={T.stam(x) for x in EXTRA_STOP}|{'groots','nieuw'}
    def sleutel(t):
        k=cache.get(t)
        if k is None:
            f=T.fold(t)
            k=T.stam(f) if 4<=len(f)<=30 and f.isalpha() and f not in EXTRA_STOP else ''
            cache[t]=k
        return k
    # ---- ronde 1: hoe vaak, waar, en lijkt het een naam ----
    import pickle; CACHE=os.path.join(WERK,'teksten','verkenner_r1.pkl')
    if os.path.exists(CACHE) and os.environ.get('RZ_VERS')!='1':
        df,ddom,dgeb,vorm,titel,hoofd,N,NDOMU,NGEBU=pickle.load(open(CACHE,'rb')); bronnen=[]
    else:
        df=collections.Counter(); ddom=collections.Counter(); dgeb=collections.Counter(); vorm=collections.defaultdict(collections.Counter)
        titel=collections.Counter(); hoofd=collections.Counter(); N=0; NDOMU=[0]*NDOM; NGEBU=[0]*len(GL); bronnen=eenheden()
    for bron,i,y,d,g,f,x,_ in bronnen:
        N+=1; toks=re.findall(r'[^\W\d_]+',tekst(x)); ks=set(); vorige=''
        if d>=0: NDOMU[d]+=1
        gg=[b for b in range(len(GL)) if g>>b&1]
        for b in gg: NGEBU[b]+=1
        for t in toks:
            k=sleutel(t)
            if k:
                ks.add(k)
                if len(vorm[k])<40 or t in vorm[k]: vorm[k][t]+=1
                if vorige in TITEL: titel[k]+=1
                if t[0].isupper(): hoofd[k]+=1
            vorige=t.lower()
        for k in ks:
            df[k]+=1
            if d>=0: ddom[k,d]+=1
            for b in gg: dgeb[k,b]+=1
    if bronnen: pickle.dump((df,ddom,dgeb,dict(vorm),titel,hoofd,N,NDOMU,NGEBU),open(CACHE,'wb'))
    print(N,'eenheden',len(df),'woorden')
    pd=np.array(NDOMU,float)/sum(NDOMU); pg=np.array(NGEBU,float)/max(1,sum(NGEBU))
    def kl(c,p):
        c=np.array(c,float)+0.5; q=c/c.sum(); return float((q*np.log(q/p)).sum())
    kand=[]
    for k,n in df.items():
        if n<25 or n>0.15*N or k in EXTRA_STOP or k in STOPK: continue
        if titel[k]>=3 and titel[k]/n>0.02: continue                     # staat vaak na mevrouw/heer/collega: een persoon
        if k in pers and k not in plek: continue
        v=vorm[k].most_common(1)[0][0]
        if v.lower() in pers and k not in plek: continue
        tot=sum(vorm[k].values()) or 1
        if hoofd[k]/tot>0.6 and not (k in plek or k in straat or (v.isupper() and 2<=len(v)<=6) or (len(v)>=8 and ACHTER.search(T.fold(v)))): continue
        if T.fold(v).startswith('gebied') and v[6:7].isupper(): continue
        s=math.log(n)*(kl([ddom[k,d] for d in range(NDOM)],pd)+0.6*kl([dgeb[k,b] for b in range(len(GL))],pg))
        kand.append((s,k))
    kand.sort(reverse=True)
    voc=[k for _,k in kand[:NV]]
    for k in plek:
        if df[k]>=10 and k not in voc: voc.append(k)
    # onderwerpen als eigen knopen
    import showcase as SC
    OND=[(SLUG(n),n,pp) for n,pp in OW.actief()]+[('parkeren','Parkeren',[SC.CONFIG['parkeren']['rx']])]
    ORX=re.compile('|'.join(f'(?P<o{i}>\\b(?:{"|".join(pp)}))' for i,(_,_,pp) in enumerate(OND)))
    knopen=[{'id':'o:'+s,'label':n,'soort':'onderwerp','slug':s} for s,n,_ in OND]
    for k in voc:
        v=vorm[k].most_common(3); lab=v[0][0]
        if hoofd[k]<0.5*df[k] or lab.isupper(): lab=lab if lab.isupper() and len(lab)<=5 else lab.lower()
        knopen.append({'id':'w:'+k,'label':lab,'soort':'plek' if k in plek else 'woord','k':k})
    idx={n['id']:i for i,n in enumerate(knopen)}; V=len(knopen); wi={k:idx['w:'+k] for k in voc}
    print(V,'knopen')
    # ---- ronde 2: verbanden en filters ----
    paar=[]; vensters=0; nv=np.zeros(V,np.int64); PB=np.zeros(V*V if V<5000 else 1,np.int64)
    jr=np.zeros((V,len(JAREN)),np.int32); dmt=np.zeros((V,NDOM),np.int32); gbt=np.zeros((V,len(GL)),np.int32); frt=collections.Counter()
    jg=collections.Counter(); jd=collections.Counter(); jf=collections.Counter(); vb={}
    for bron,i,y,d,g,f,x,meta in eenheden():
        if y not in JAREN: continue
        yi=JAREN.index(y); t=tekst(x); ft=T.fold(t); gg=[b for b in range(len(GL)) if g>>b&1]
        inunit=set(); pos=0
        while pos<len(ft):
            e=ft.find(' ',pos+VENSTER); e=len(ft) if e<0 else e; w=ft[pos:e]
            ids={wi[k] for k in (T.stam(z) for z in re.findall(r'[a-z]+',w)) if k in wi}
            ids|={idx['o:'+OND[int(m.lastgroup[1:])][0]] for m in ORX.finditer(w)}
            if ids:
                vensters+=1; a=np.fromiter(ids,np.int64); nv[a]+=1
                if len(a)>1:
                    a.sort(); I,J=np.triu_indices(len(a),1); paar.append(a[I]*V+a[J])
                inunit|=ids
                if bron=='d' and meta[2] and not meta[2].lower().startswith('inspreker') and y>='2022':
                    for n in ids:
                        sc=(not meta[3][4])*2+bool(f>=0)+int(y)/10000
                        if n not in vb or sc>vb[n][0]:
                            kk=knopen[n].get('k'); m=re.search(r'\b'+re.escape(kk),w) if kk else (ORX.search(w))
                            if m:
                                s0=max(0,pos+m.start()-120); s1=min(len(t),pos+m.end()+120)
                                vb[n]=(sc,{'f':('…' if s0 else '')+re.sub(r'\s+',' ',t[s0:s1]).strip()+'…','w':meta[2],'p':PAR[f] if f>=0 else '','d':meta[0][0],'v':meta[0][2],'pt':meta[1][2][:120]})
            pos=e+1
            if len(paar)>2000: PB+=np.bincount(np.concatenate(paar),minlength=V*V); paar=[]
        if not inunit: continue
        a=np.fromiter(inunit,np.int64); jr[a,yi]+=1
        if d>=0: dmt[a,d]+=1
        for b in gg: gbt[a,b]+=1
        for n in inunit:
            for b in gg: jg[n,yi,b]+=1
            if d>=0: jd[n,yi,d]+=1
            if f>=0: jf[n,yi,f]+=1
    if paar: PB+=np.bincount(np.concatenate(paar),minlength=V*V)
    C=PB.reshape(V,V); C=C+C.T
    print(vensters,'vensters')
    # ---- sterkste verbanden ----
    p=nv/vensters; Pij=C/vensters
    with np.errstate(divide='ignore',invalid='ignore'):
        npmi=np.where(C>=8,np.log(Pij/np.outer(p,p))/-np.log(np.maximum(Pij,1e-12)),0)
    sc=npmi*np.log1p(C)
    E={}
    for i in range(V):
        for j in np.argsort(-sc[i])[:TOP]:
            if sc[i,j]>0: E[min(i,j),max(i,j)]=(round(float(npmi[i,j]),3),int(C[i,j]))
    print(len(E),'verbanden')
    # weg met losse knopen
    deg=collections.Counter()
    for a,b in E: deg[a]+=1; deg[b]+=1
    houd=[i for i in range(V) if deg[i] and nv[i]>=10]; nieuw={o:n for n,o in enumerate(houd)}
    # ---- domeinkleur per knoop ----
    pdm=dmt.sum(0)/dmt.sum()
    for i,n in enumerate(knopen):
        q=(dmt[i]+0.5)/(dmt[i]+0.5).sum(); n['dom']=int(np.argmax(q*np.log(q/pdm)))
    # ---- indeling ----
    M=len(houd)
    ea=np.array([[nieuw[a],nieuw[b],w] for (a,b),(w,c) in E.items() if a in nieuw and b in nieuw],float)
    X=np.zeros((M,2))
    # ---- uitvoer ----
    uit_n=[]
    for o in houd:
        n=knopen[o]; i=nieuw[o]
        r={'id':n['id'],'l':n['label'],'s':n['soort'][0],'x':round(float(X[i,0]),1),'y':round(float(X[i,1]),1),'n':int(nv[o]),'dom':n['dom'],
           'j':jr[o].tolist(),'dm':dmt[o].tolist(),'g':gbt[o].tolist()}
        if n.get('slug'): r['slug']=n['slug']
        uit_n.append(r)
    sp=lambda cnt:{str(nieuw[n]):[[a,b,c] for (nn,a,b),c in cnt.items() if nn==n] for n in houd}
    def sparse(cnt):
        per=collections.defaultdict(list)
        for (n,a,b),c in cnt.items():
            if n in nieuw: per[nieuw[n]].append([a,b,c])
        return [per.get(i,[]) for i in range(M)]
    uit={'stand':STAND,'jaren':JAREN,'dom':dm['dom'],'geb':GL,'par':PAR,'n':N,'vensters':vensters,
         'knopen':uit_n,'e':[[nieuw[a],nieuw[b],w,c] for (a,b),(w,c) in E.items() if a in nieuw and b in nieuw],
         'jg':sparse(jg),'jd':sparse(jd),'jf':sparse(jf)}
    uit=grootste(uit)
    e=np.array([[a,b,w] for a,b,w,c in uit['e']],float); X=fa2(len(uit['knopen']),e[:,0].astype(int),e[:,1].astype(int),e[:,2])
    for k,(x,y) in zip(uit['knopen'],X.tolist()): k['x']=round(x,1); k['y']=round(y,1)
    json.dump(uit,open(os.path.join(DOCS,'verkenner.json'),'w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
    json.dump({knopen[o]['id']:vb[o][1] for o in houd if o in vb},open(os.path.join(DOCS,'verkenner-vb.json'),'w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
    print(M,'knopen',len(uit['e']),'verbanden',os.path.getsize(os.path.join(DOCS,'verkenner.json'))//1000,'kB')
    print('voorbeeld:',[n['l'] for n in sorted(uit_n,key=lambda n:-n['n'])[:80]])
if __name__=='__main__':
    import sys
    herindeel() if sys.argv[1:2]==['indeling'] else main()
