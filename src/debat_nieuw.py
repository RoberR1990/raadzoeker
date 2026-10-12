# Nieuwe debatten automatisch toevoegen: raads- en commissievergaderingen die na de eenmalige verzameling zijn gehouden.
#   python src/debat_nieuw.py [--dagen 60]   -> vult docs/data/raad/JAAR.zst en docs/data/commissies/JAAR.zst aan (+ meta.json)
# Daarna debat_index.py draaien (zoekindex 'Gezegd'; daar leest ook verg_batch.py uit).
# Bron per vergadering: iBabs-kalender -> agendapagina (agendapunten, sprekerstijdlijn, video-id) -> Company Webcast-ondertiteling
# (openbaar: /players/<code>/info geeft het speler-id, /players/<id>/vtt/ de lijst, /players/<id>/vtt/<pad>/<taal> de tekst).
# Werkt zoals de 'gap-fill' in emit.py en emit_comm.py: tekst = automatische ondertiteling (k=4), per spreker x agendapunt geknipt op de tijdlijn.
# Alleen aanvullen: bestaande vergaderingen en indexen blijven gelijk (labels als 'r:2026:<i>' blijven geldig). Vergaderingen zonder
# (voldoende) ondertiteling worden overgeslagen en bij een volgende run opnieuw geprobeerd. Ruwe gegevens per vergadering in WERK/debat_nieuw/.
# Let op: 'python src/maak.py alles' bouwt uit de oude bronbestanden en laat deze vergaderingen weg; draai dit script daarna opnieuw.
import json,os,re,sys,html,datetime,urllib.request,zstandard
import ibabs, toez
from bs4 import BeautifulSoup
from tijdlijn import key,parse_tl,PARTY
from paden import DOCS,WERK
B='https://gemeenteraad.rotterdam.nl'; CWC='https://sdk.companywebcast.com'
RAADTYPE='100002367'
MND={m:i+1 for i,m in enumerate('januari februari maart april mei juni juli augustus september oktober november december'.split())}
SKIP=re.compile(r'procedurevergadering|presidium|agendacommissie|werkgeverscommissie|auditcommissie|seniorenconvent|fractievoorzitters|besloten|vervallen',re.I)
ROLES=['raadslid','voorzitter','wethouder','burgemeester','griffier','overig']
VOORV=re.compile(r'^(VAN DER|VAN DEN|VAN DE|VAN|DE|DEN|EL|TER|LA) ')
RUW=os.path.join(WERK,'debat_nieuw')

def kalender(van,tot):
    """{agendaId: (datum, label, agendatype)} voor vergaderingen tussen van en tot (iBabs-kalender per maand)."""
    uit={}; d=van.replace(day=1)
    while d<=tot:
        h=ibabs.get(B+f'/Calendar/GetMonthAgendas?month={d.month-1}&year={d.year}',cache=False)
        for aid,tid,lab,dag in re.findall(r'href="/Agenda/Index/([0-9a-f-]+)"[^>]*data-agendatype-id="(\d+)"[^>]*>\s*<div class="calendar-item-label">\s*([^<]+?)\s*(?:<span.*?)?</div>\s*<div class="sr-only">\s*\w+ (\d+ \w+ \d{4})',h,re.S):
            g,m,j=dag.split(); dt=datetime.date(int(j),MND[m],int(g))
            if van<=dt<=tot: uit[aid]=(dt.isoformat(),re.sub(r'^zzz ','',html.unescape(lab).strip()),tid)
        d=(d+datetime.timedelta(days=32)).replace(day=1)
    return uit

def agenda(aid):
    """Agendapunten met sprekerstijdlijn en het video-id van de agendapagina (zoals agenda.py)."""
    s=ibabs.get(B+f'/Agenda/Index/{aid}',cache=False)
    s=re.sub(r'src="data:[^"]*"','src=""',s)
    vid=re.search(r'data-video-id="([^"]*)"',s); vt=re.search(r'data-video-type="([^"]*)"',s)
    i=s.find('id="agendaitems"'); soup=BeautifulSoup(s[i-200:] if i>0 else s,'lxml'); items=[]
    for it in soup.select('div.agenda-item'):
        nr=it.select_one('.panel-id'); tl=it.select_one('.panel-title-label')
        sp=[' '.join(o.get_text().split()) for o in it.select('div.speakers > div.offset')]
        items.append({'nr':nr.get_text(strip=True) if nr else '','title':' '.join(tl.get_text().split()) if tl else '','sp':sp})
    return (vid.group(1) if vid else ''),(vt.group(1) if vt else ''),items

def haal(url):
    req=urllib.request.Request(url,headers={'User-Agent':ibabs.UA})
    with urllib.request.urlopen(req,timeout=120) as r: return r.read().decode('utf8','replace')

def ondertitels(code):
    """[(seconde, tekst)] uit de Company Webcast-ondertiteling, of None als die (nog) ontbreekt."""
    info=json.loads(haal(f'{CWC}/players/{code.replace("/","_")}/info'))
    lijst=json.loads(haal(f'{CWC}/players/{info["id"]}/vtt/'))
    if not lijst: return None,info
    v=next((x for x in lijst if x.get('id')=='nl'),lijst[0])
    t=haal(f'{CWC}/players/{info["id"]}/vtt/{v["path"]}/{v["id"]}')
    cs=[];last=None   # zelfde opschoning als harvest.js + subs.cues
    for m in re.finditer(r'(\d+):(\d\d):(\d\d)\.\d+ --> [^\n]*\n([\s\S]*?)(?:\r?\n\r?\n|$)',t):
        x=re.sub(r'\s*\r?\n\s*',' ',re.sub(r'<v [^>]*>','',m.group(4))).strip()
        if x==last and 'vergadering begint' in x: continue
        last=x; cs.append((int(m.group(1))*3600+int(m.group(2))*60+int(m.group(3)),x))
    return cs,info

def secs(t): hh,mm,ss=map(int,t.split(':')); return hh*3600+mm*60+ss

class Bron:
    """Eén jaardata-map (raad of commissies): bestaande jaren laden, vergaderingen toevoegen, terugschrijven."""
    def __init__(self,naam):
        self.dir=os.path.join(DOCS,'data',naam); self.meta=json.load(open(os.path.join(self.dir,'meta.json'),encoding='utf8'))
        self.jaren={}; self.gewijzigd=set()
        self.spk={d:i for i,(d,_) in enumerate(self.meta['spk'])}; self.par={p:i for i,p in enumerate(self.meta['par'])}
        self.sort={}
        for i,(d,s) in enumerate(self.meta['spk']): self.sort.setdefault(s,[]).append(i)
        for y in self.meta['years']: self.jaar(y['y'])
    def jaar(self,y):
        if y not in self.jaren:
            p=os.path.join(self.dir,f'{y}.zst')
            self.jaren[y]=json.loads(zstandard.ZstdDecompressor().decompress(open(p,'rb').read(),max_output_size=1<<30)) if os.path.exists(p) else \
                {'M':[],'D':[],'I':[],'s':{k:[] for k in('m','i','k','sp','pa','ro','pg','d','z','t','v')},'mo':[],'tz':[],'sm':{}}
        return self.jaren[y]
    def bekend(self):
        ids=set(); vids=set()
        for Y in self.jaren.values():
            for M in Y['M']:
                if M[1]: ids.add(M[1])
                if len(M)>4 and M[4]: vids.add(M[4])
        return ids,vids
    def spreker(self,o):
        """Index in meta.spk; hergebruikt een bestaande naam (zelfde achternaamsleutel en voorletter/voornaam), anders nieuw zoals emit_comm."""
        if o['sur']:
            k=key(o['sur']); sort=VOORV.sub('',k)
            vn=(o.get('first') or '').lower(); vl=(o.get('init') or '')[:1].upper()
            for i in reversed(self.sort.get(sort,[])):
                d=self.meta['spk'][i][0]
                if key(d).endswith(k) and ((vn and d.lower().startswith(vn+' ')) or (not vn and vl and d[:1].upper()==vl)): return i
            disp=((o['first']+' ') if o.get('first') else ((o['init'].strip()+' ') if o.get('init') else ''))+o['sur']
        else:
            g=o.get('generic',''); disp='Voorzitter' if o['role']=='voorzitter' else (g[:1].upper()+g[1:] if g else 'Onbekende spreker'); sort=disp.upper()
        if disp not in self.spk:
            self.spk[disp]=len(self.meta['spk']); self.meta['spk'].append([disp,sort]); self.sort.setdefault(sort,[]).append(self.spk[disp])
        return self.spk[disp]
    def partij(self,p):
        if p is None: return -1
        if p not in self.par: self.par[p]=len(self.meta['par']); self.meta['par'].append(p)
        return self.par[p]
    def voeg_toe(self,datum,aid,label,vref,items,cs):
        y=datum[:4]; Y=self.jaar(y); S=Y['s']; mi=len(Y['M']); n0=len(S['t'])
        Y['M'].append([datum,aid,label,2,vref])
        imap={}
        for k,it in enumerate(items): imap[k]=len(Y['I']); Y['I'].append([mi,it['nr'].strip().rstrip('.'),it['title'][:400]])
        ent=[]
        for k,it in enumerate(items):
            for t in it['sp']:
                o=parse_tl(t)
                if o: o['item']=k; ent.append(o)
        turns=[];last=None
        for o in sorted(ent,key=lambda o:secs(o['t'])):
            w=(self.spreker(o),self.partij(o['party']),ROLES.index(o['role'])); kt=(o['item'],w[0])
            if kt==last: continue
            last=kt; turns.append((secs(o['t']),o['item'],w))
        def add(ii,sp,pa,ro,sec,text):
            for c,v in zip(('m','i','k','sp','pa','ro','pg','d','z','t','v'),(mi,ii,4,sp,pa,ro,sec,-1,0,text,sec)): S[c].append(v)
        import bisect
        ct=[c[0] for c in cs]
        if turns:
            segs=[]
            for n,(s0,it,w) in enumerate(turns):
                en=turns[n+1][0] if n+1<len(turns) else 10**9
                lo=bisect.bisect_left(ct,s0-2 if n else -1); hi=bisect.bisect_left(ct,en-2)
                tx=' '.join(c[1] for c in cs[lo:hi]).strip()
                if tx: segs.append((it,s0,w,tx))
            for it,s0,w,tx in sorted(segs,key=lambda x:(x[0],x[1])): add(imap[it],w[0],w[1],w[2],s0,tx)
        else:
            ii=len(Y['I']); Y['I'].append([mi,'','Uitzending (geen sprekerstijdlijn)'])
            buf=[];s0=None
            for t,x in cs:
                if s0 is None: s0=t
                buf.append(x)
                if (t-s0>=75 and re.search(r'[.?!]$',x)) or t-s0>150: add(ii,-1,-1,5,s0,' '.join(buf)); buf=[];s0=None
            if buf: add(ii,-1,-1,5,s0,' '.join(buf))
        # toezeggingen op formulering (zoals emit.py/emit_comm.py), alleen voor de nieuwe beurten van wethouders/burgemeester
        for i in range(n0,len(S['t'])):
            t=S['t'][i]
            if S['ro'][i] in(2,3) and S['sp'][i]>=0:
                hard=toez.find(t) if 'toe' in t else []
                for a_,b_ in hard: Y['tz'].append([i,a_,b_,0])
                for a_,b_ in toez.find(t,toez.P2):
                    if not any(a_<hb and b_>ha for ha,hb in hard): Y['tz'].append([i,a_,b_,1])
        self.gewijzigd.add(y)
        return len(S['t'])-n0,len(turns)
    def schrijf(self):
        if not self.gewijzigd: return
        zc=zstandard.ZstdCompressor(level=22)
        for y in sorted(self.gewijzigd):
            Y=self.jaren[y]; raw=json.dumps(Y,ensure_ascii=False,separators=(',',':')).encode('utf8'); z=zc.compress(raw)
            open(os.path.join(self.dir,f'{y}.zst'),'wb').write(z)
            e=next((x for x in self.meta['years'] if x['y']==y),None)
            if e is None: e={'y':y}; self.meta['years'].append(e); self.meta['years'].sort(key=lambda x:x['y'])
            e.update({'raw':len(raw),'z':len(z),'meet':len(Y['M']),'notulen':sum(1 for m in Y['M'] if m[3]==1),'seg':len(Y['s']['t'])})
            e.pop('h',None)
        if 'cats' in self.meta: self.meta['cats']=sorted({m[2] for Y in self.jaren.values() for m in Y['M']})
        json.dump(self.meta,open(os.path.join(self.dir,'meta.json'),'w',encoding='utf8'),ensure_ascii=False)

def main(dagen=60):
    tot=datetime.date.today()-datetime.timedelta(days=1); van=tot-datetime.timedelta(days=dagen)
    R=Bron('raad'); C=Bron('commissies')
    ids=set(); vids=set()
    for X in (R,C):
        a,b=X.bekend(); ids|=a; vids|=b
    os.makedirs(RUW,exist_ok=True); n=0; overslaan=[]
    for aid,(datum,label,tid) in sorted(kalender(van,tot).items(),key=lambda x:x[1]):
        if aid in ids or SKIP.search(label): continue
        p=os.path.join(RUW,aid[:8]+'.json')
        try:
            vid,vt,items=agenda(aid)
            if not vid or vt!='Cwc': overslaan.append((datum,label,'geen video' if not vid else 'video '+vt)); continue
            vref='c:'+vid
            if vref in vids: continue   # zelfde uitzending staat al bij een andere vergadering
            cs,info=ondertitels(vid)
            if not cs or len(cs)<=20: overslaan.append((datum,label,'nog geen ondertiteling')); continue
        except ibabs.Blokkade: raise
        except Exception as e:
            overslaan.append((datum,label,f'fout: {e!s:.80}')); continue
        json.dump({'aid':aid,'datum':datum,'label':label,'type':tid,'video':vid,'items':items,'cues':cs},open(p,'w',encoding='utf8'),ensure_ascii=False)
        raad=tid==RAADTYPE
        X=R if raad else C
        nseg,nturn=X.voeg_toe(datum,aid,'' if raad else label,vref,items,cs)
        ids.add(aid); vids.add(vref); n+=1
        print(f'+ {datum} {label}: {nseg} fragmenten, {nturn} sprekerswissels{"" if nturn else " (geen sprekerstijdlijn)"}',flush=True)
    for d,l,r in overslaan: print(f'- {d} {l}: {r}')
    R.schrijf(); C.schrijf()
    print(n,'vergaderingen toegevoegd')
if __name__=='__main__':
    a=sys.argv[1:]; main(int(a[a.index('--dagen')+1]) if '--dagen' in a else 60)
