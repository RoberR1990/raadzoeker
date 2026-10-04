# Fase 2: gebieden.
#   python src/gebieden.py   -> WERK/gebied/gebieden.json (hiërarchie + organen + vertaaltabel), WERK/labels/gebied.json, gebied_rapport.txt
# 2a hiërarchie: stad -> 14 gebieden -> 71 wijken (Wijkprofiel) -> CBS-buurten (2024)
# 2b organen: gebiedscommissies/wijkcomités (tot 2022) en wijkraden (vanaf 2022), met de wijken die ze bestrijken en een vertaaltabel
# 2c koppelen, drie methodes:
#   bron     wijkraadstukken en -vergaderingen horen bij hun wijkraad (zeker)
#   locatie  bekendmakingen met een locatiepunt -> buurt -> wijk (zeker)
#   tekst    wijk-, gebieds- en straatnamen (BAG) in titel of tekst van raadsstukken en in debatten ('genoemd in', onzeker)
import json,os,re,glob,collections,random,zstandard
from paden import WERK,DOCS
import wijken as W, themes, domeinen as D, bag_straten as BS

G=os.path.join(WERK,'gebied')
STOP_STRAAT={'Coolsingel',   # staat in de praktijk voor het stadhuis, niet voor de straat
  'Nieuwe Maas','Oude Maas','Nieuwe Waterweg','Het Scheur','Calandkanaal','Hartelkanaal','Beerkanaal'}   # water door meerdere gebieden
def achternamen():
    """achternamen van sprekers (raadsleden, wethouders): een straat met dezelfde naam is vaak de persoon"""
    out=set()
    for k in ('raad','commissies'):
        for naam,_ in json.load(open(os.path.join(DOCS,'data',k,'meta.json'),encoding='utf8'))['spk']:
            w=naam.split()
            if w: out.add(w[-1])
    return out
PERSOON=re.compile(r'^(?:[A-Z]\.)+$|\)$|^(wethouder|burgemeester|heer|mevrouw|mevr\.|dhr\.|lid|leden|collega|raadslid)$',re.I)

def norm_raad(s): return re.sub(r'\s*\((in)?formeel\)','',(s or '').split(' · ')[0]).strip()

def hierarchie():
    WW=json.load(open(os.path.join(WERK,'wijk','wijken.json'),encoding='utf8'))
    B=json.load(open(os.path.join(WERK,'kaart','buurten_2024.json'),encoding='utf8'))['features']
    bnaam={f['properties']['buurtcode']:f['properties']['buurtnaam'] for f in B}; bwk={f['properties']['buurtcode']:f['properties']['wijkcode'] for f in B}
    NB={W.n(v):k for k,v in bnaam.items()}
    rows=[dict(id='rotterdam',naam='Rotterdam',niveau='stad',ouder=None,code='GM0599',geldig_van='2014',geldig_tot=None)]
    wijk_b={}; b_wijk=collections.defaultdict(list); wijk_g={}
    for g,ws in WW.items():
        for s,naam in ws.items():
            bb=[NB[W.n(x)] for x in W.BUURT.get(s,[naam]) if W.n(x) in NB]
            wijk_b[s]=bb; wijk_g[s]=g
            for b in bb: b_wijk[b].append(s)
    gcode={}
    for g in WW:
        c=collections.Counter(bwk[b] for s in WW[g] for b in wijk_b[s]); gcode[g]=c.most_common(1)[0][0] if c else None
        rows.append(dict(id=g,naam=W.GEBNAAM.get(g,g.capitalize()),niveau='gebied',ouder='rotterdam',code=gcode[g],geldig_van='2014',geldig_tot=None))
    for g,ws in WW.items():
        for s,naam in ws.items():
            rows.append(dict(id=s,naam=naam.replace(' (wijk)',''),niveau='wijk',ouder=g,code=f'wijkprofiel:{g}/{s}',geldig_van='2014',geldig_tot=None))
    wk_g={v:k for k,v in gcode.items() if v}
    for b,naam in sorted(bnaam.items()):
        ws=b_wijk.get(b,[])
        rows.append(dict(id=b,naam=naam,niveau='buurt',ouder=ws[0] if ws else wk_g.get(bwk[b],'rotterdam'),ook=ws[1:] or None,code=b,geldig_van='2022',geldig_tot=None))
    return rows,WW,wijk_b,b_wijk,wijk_g

def organen(WW,wijk_g):
    V=[json.loads(l) for l in open(os.path.join(WERK,'wijk','wijkraadvergaderingen.jsonl'),encoding='utf8') if l.strip()]
    dat=collections.defaultdict(list)
    for v in V:
        if v.get('datum'): dat[norm_raad(v['raad'])].append(v['datum'])
    GEBC={'Rotterdam Centrum':'rotterdam-centrum'}
    org={}
    for naam in set(norm_raad(v['raad']) for v in V):
        if naam.startswith('Wijkraadverkiezing'): continue
        d=sorted(dat.get(naam,[]))
        if naam.startswith('Gebiedscommissie'):
            g=naam.replace('Gebiedscommissie ',''); g=GEBC.get(g,W.n(g).replace(' ','-'))
            ws=[s for s in WW.get(g,{})]; soort='gebiedscommissie'
        else:
            ws=W.RAAD.get(naam,[]); soort='wijkcomité' if naam.lower().startswith('wijkcomit') else 'dorpsraad' if naam.startswith('Dorpsraad') else 'wijkraad'
        oud=soort in('gebiedscommissie','wijkcomité') or (d and d[-1]<'2022-05')
        org[naam]=dict(naam=naam,soort=soort,periode='tot 2022' if oud else 'vanaf 2022',van=d[0] if d else None,tot=d[-1] if d else None,
                       wijken=ws,gebieden=sorted({wijk_g[s] for s in ws if s in wijk_g}))
    # dezelfde wijkraad onder een andere naam (bijv. 'Bergpolder-Blijdorp-Liskwartier' en 'Blijdorp-Bergpolder-Liskwartier'): samenvoegen
    per=collections.defaultdict(list)
    for o in org.values():
        if o['periode']=='vanaf 2022': per[frozenset(o['wijken'])].append(o)
    for oo in per.values():
        oo.sort(key=lambda o:o['tot'] or '')
        for o in oo[:-1]: o['zelfde_als']=oo[-1]['naam']; oo[-1].setdefault('ook_genoemd',[]).append(o['naam'])
    # Carnisse-Zuiderpark (tot 2023) is uitgebreid met Zuidplein
    for o in org.values():
        if o['periode']=='vanaf 2022' and not o.get('zelfde_als') and o['tot'] and o['tot']<'2024':
            groter=[n for n in org.values() if n is not o and n['periode']=='vanaf 2022' and not n.get('zelfde_als') and set(o['wijken'])<set(n['wijken'])]
            if groter: o['opgevolgd_door']=groter[0]['naam']
    # vertaaltabel oud -> nieuw op overlap van wijken
    nieuw=[o for o in org.values() if o['periode']=='vanaf 2022' and not o.get('zelfde_als') and not o.get('opgevolgd_door')]; vt=[]
    for o in org.values():
        if o['periode']!='tot 2022': continue
        ov=[(n['naam'],sorted(set(o['wijken'])&set(n['wijken']))) for n in nieuw if set(o['wijken'])&set(n['wijken'])]
        if not ov: soort='geen opvolger gevonden'
        elif len(ov)==1 and set(ov[0][1])==set(o['wijken'])==set(next(n for n in nieuw if n['naam']==ov[0][0])['wijken']): soort='één op één'
        elif len(ov)==1 and set(ov[0][1])==set(o['wijken']): soort='opgegaan in grotere wijkraad'
        elif all(set(w)<=set(o['wijken']) for _,w in ov) and len(ov)>1 and set().union(*[set(next(n for n in nieuw if n['naam']==x)['wijken']) for x,_ in ov])<=set(o['wijken']): soort='opgesplitst'
        else: soort='grenzen lopen niet gelijk'
        vt.append(dict(oud=o['naam'],nieuw=[x for x,_ in ov],soort=soort,overlap={x:w for x,w in ov},niet_gedekt=sorted(set(o['wijken'])-set().union(*[set(w) for _,w in ov])) if ov else o['wijken']))
    return org,vt

def wijkregex(WW):
    """[(wijk- of gebiedsslug, gecompileerde regex op gevouwen tekst)]"""
    out=[]
    for g,ws in WW.items():
        for s,naam in ws.items():
            zoek=W.ZOEK.get(s,[naam]) if s in W.ZOEK else [naam]
            if not zoek or zoek==['Cool']: continue
            out.append((s,re.compile('|'.join(z[3:] if z.startswith('re:') else r'(?<![a-z0-9])'+re.escape(W.fold(z))+r'(?![a-z0-9])' for z in zoek))))
    TG={t[0]:t[1] for t in themes.T[2][1]}
    for g in WW:
        naam=W.GEBNAAM.get(g,g.capitalize())
        terms=TG.get(naam)
        if not terms: continue
        # alleen de gebiedsnaam zelf (de wijknamen in het thema vangen we al per wijk); 'Noord' is te dubbelzinnig
        eigen=[t.strip() for t in terms.split('|')][:1]
        if naam=='Noord': eigen=['rotterdam-noord','rotterdam noord']
        out.append((g,re.compile('|'.join(r'(?<![a-z0-9])'+re.escape(W.fold(e.strip('"')))+r'(?![a-z0-9])' for e in eigen))))
    return out

def straatzoeker(b_wijk):
    p=os.path.join(G,'straten.json')
    if not os.path.exists(p): return None,{}
    S=json.load(open(p,encoding='utf8')); namen={}; pers=achternamen()
    for s,v in S.items():
        if s in STOP_STRAAT or s in pers or len(s)<7 or ' ' not in s and not re.search(r'(straat|weg|laan|plein|kade|singel|dijk|dreef|hof|park|pad|steeg|gracht|haven|baan|plaats|wal|veld|boulevard|kwartier|markt|erf|ring|brug|tunnel|polder|oord|dam|kanaal|vliet|lei|waard)$',s.lower()): continue
        tot=sum(v['buurten'].values()); ws=collections.Counter()
        for b,n in v['buurten'].items():
            for w in b_wijk.get(b,[]): ws[w]+=n
        # wijken met minstens 20% van de adressen aan die straat
        namen[s]=[w for w,n in ws.items() if n>=.2*tot]
    eerste=collections.defaultdict(set)
    for s in namen: eerste[s.split(' ')[0]].add(s)
    def zoek(t):
        tok=t.split(); hits=collections.Counter()
        for i,w in enumerate(tok):
            w=w.strip('.,;:()"“”‘’!?')
            if w not in eerste or (i and PERSOON.search(tok[i-1])): continue
            for k in range(5,0,-1):
                kand=' '.join(x.strip('.,;:()"“”‘’!?') for x in tok[i:i+k])
                if kand in eerste[w] or (k==1 and w in namen): hits[kand if kand in namen else w]+=1; break
        return hits
    return zoek,namen

def main():
    random.seed(7)
    rows,WW,wijk_b,b_wijk,wijk_g=hierarchie()
    org,vt=organen(WW,wijk_g)
    os.makedirs(G,exist_ok=True)
    json.dump({'gebieden':rows,'organen':list(org.values()),'vertaling':vt},open(os.path.join(G,'gebieden.json'),'w',encoding='utf8'),ensure_ascii=False,indent=1)
    rep=['2a Hiërarchie: '+', '.join(f'{k} {v}' for k,v in collections.Counter(r['niveau'] for r in rows).items())]
    zonder=[r['naam'] for r in rows if r['niveau']=='buurt' and r['ouder'] in WW|{'rotterdam':0}]
    rep.append(f'  CBS-buurten zonder wijk (haven/bedrijventerrein/water): {len(zonder)}: {", ".join(zonder)}')
    rep.append('  CBS-buurt in meer dan één wijk: '+', '.join(f"{r['naam']} ({r['ouder']}, {', '.join(r['ook'])})" for r in rows if r.get('ook')))
    rep.append('  Wijken met meer dan één CBS-buurt: '+', '.join(f'{s} ({len(b)})' for s,b in wijk_b.items() if len(b)>1))
    rep.append('\n2b Organen: '+', '.join(f'{k} {v}' for k,v in collections.Counter((o['soort'],o['periode']) for o in org.values()).items()))
    for v in sorted(vt,key=lambda v:v['soort']): rep.append(f"  {v['oud']:45} -> {v['soort']}: {'; '.join(v['nieuw'])}"+(f"  (niet gedekt: {', '.join(v['niet_gedekt'])})" if v['niet_gedekt'] else ''))
    nw=set().union(*[set(o['wijken']) for o in org.values() if o['periode']=='vanaf 2022'])
    rep.append('  Wijken zonder wijkraad vanaf 2022: '+', '.join(s for s in wijk_g if s not in nw))
    # ---- 2c koppelen
    lab=collections.defaultdict(list)   # sleutel -> [[slug, methode, aantal]]
    m,tekst=D.tekstdocs(); S=m['soorten']
    alias={o['naam']:o['wijken'] for o in org.values()}
    kort={W.n(re.sub(r'^(Wijkraad|Dorpsraad|Wijkcomit[eé]|Gebiedscommissie)\s+','',k,flags=re.I)):v for k,v in alias.items()}
    WR=wijkregex(WW); zoekstraat,namen=straatzoeker(b_wijk)
    WIJKRAAD=('Wijkraadstuk','Wijkraadvergadering','Wijkraadadvies','Ongevraagd wijkraadadvies','Wijkverslag','Wijkakkoord of wijkplan','Collegereactie op wijkplan')
    ctx={}   # voor de steekproef: sleutel -> (term, fragment)
    def tekstlabels(k,titel,tx):
        f=W.fold(titel+' \n '+tx); gev=collections.Counter(); voorbeeld=None
        for s,r in WR:
            n=len(r.findall(f))
            if n: gev[s]+=n; voorbeeld=voorbeeld or (s,r.search(f))
        hs={}
        if zoekstraat:
            hs=zoekstraat(titel+' \n '+tx)
            for st,n in hs.items():
                for w in namen.get(st,[]): gev[w]+=n
        for s,n in gev.items(): lab[k].append([s,'tekst',n])
        if gev:
            # één willekeurige treffer bewaren voor de controle
            if hs and random.random()<.5:
                st=random.choice(list(hs)); p=(titel+' \n '+tx).find(st); txt=titel+' \n '+tx
                ctx[k]=(st,', '.join(namen.get(st,[])) or '-',re.sub(r'\s+',' ',txt[max(0,p-200):p+200]))
            elif voorbeeld:
                s,mm=voorbeeld; ctx[k]=(mm.group(0),s,re.sub(r'\s+',' ',f[max(0,mm.start()-200):mm.end()+200]))
    tel=collections.Counter(); totaal=collections.Counter()
    for i,r in enumerate(m['d']):
        k=f't:{i}'; s=S[r[0]]; totaal[s]+=1
        if s in WIJKRAAD:
            ws=alias.get(norm_raad(r[3])) or kort.get(W.n(norm_raad(r[3])))
            if not ws:
                mm=re.search(r'(?:wijkraad|dorpsraad|wijkcomit[eé])\s+([^,(]+?)(?:\s+(?:over|inzake|betreffende|aan|m\.b\.t\.|t\.a\.v\.)\b|[,(]|$)',r[2],re.I)
                ws=kort.get(W.n(mm.group(1))) if mm else None
            if ws:
                for w in ws: lab[k].append([w,'bron',1])
                tel[(s,'bron')]+=1; continue
        tekstlabels(k,r[2],tekst(i))
        tel[(s,'tekst' if lab.get(k) else 'geen')]+=1
    for a in D.agendapunten():
        k=a[0]; totaal[a[1]]+=1
        tekstlabels(k,a[4],a[5]); tel[(a[1],'tekst' if lab.get(k) else 'geen')]+=1
    # locatie: bekendmakingen
    R=[]
    for f in json.load(open(os.path.join(WERK,'kaart','buurten_2024.json'),encoding='utf8'))['features']:
        for rr in BS.ringen(f['geometry']): R.append((f['properties']['buurtcode'],rr,min(x for x,_ in rr),max(x for x,_ in rr),min(y for _,y in rr),max(y for _,y in rr)))
    for i,l in enumerate(open(os.path.join(WERK,'wijk','bekendmakingen.jsonl'),encoding='utf8')):
        b=json.loads(l); k=f'b:{i}'; totaal['Bekendmaking']+=1
        if b.get('lon') is None: tel[('Bekendmaking','geen locatie')]+=1; continue
        code=next((c for c,rr,a1,b1,c1,d1 in R if a1<=b['lon']<=b1 and c1<=b['lat']<=d1 and BS.binnen(b['lon'],b['lat'],rr)),None)
        ws=b_wijk.get(code,[])
        for w in ws: lab[k].append([w,'locatie',1])
        tel[('Bekendmaking','locatie' if ws else 'punt buiten een wijk')]+=1
    json.dump(lab,open(os.path.join(WERK,'labels','gebied.json'),'w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
    json.dump(ctx,open(os.path.join(G,'tekst_context.json'),'w',encoding='utf8'),ensure_ascii=False)
    rep.append('\n2c Dekking (aandeel dat minstens één wijk of gebied krijgt):')
    for s in sorted(totaal):
        d={meth:n for (ss,meth),n in tel.items() if ss==s}
        rep.append(f'  {s:28} {totaal[s]:6}  '+', '.join(f'{meth} {n} ({n/totaal[s]:.0%})' for meth,n in sorted(d.items())))
    # valkuilen
    nn=collections.Counter(len({wijk_g.get(x[0],x[0]) for x in v}) for k,v in lab.items() if any(x[1]=='tekst' for x in v))
    rep.append('\nTekstmethode: aantal verschillende gebieden per stuk: '+', '.join(f'{k}: {v}' for k,v in sorted(nn.items())))
    if namen:
        rep.append(f'Straten in de zoeklijst: {len(namen)}; straten over meer dan één wijk (>=20% adressen): {sum(1 for v in namen.values() if len(v)>1)}; over geen enkele wijk (>=20%): {sum(1 for v in namen.values() if not v)}')
    open(os.path.join(WERK,'labels','gebied_rapport.txt'),'w',encoding='utf8').write('\n'.join(rep))
    print('\n'.join(rep))

if __name__=='__main__': main()
