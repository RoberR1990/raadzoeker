# Logboek 'Wat is er nieuw' -> docs/data/logboek.json (pagina docs/nieuw.html, link achter 'bijgewerkt' in de kop).
#   python src/logboek.py voor   vóór de run: legt de huidige stand vast in WERK/logboek_voor.json
#   python src/logboek.py na     na de run: vergelijkt, en voegt alleen bij verschil een regel toe
# Bewaart alles: de laatste 7 dagen (minstens 10 regels) in logboek.json, oudere regels per maand in docs/data/logboek/JJJJ-MM.json
# (met logboek/index.json = lijst van maanden, nieuwste eerst). De pagina laadt die maanden pas bij 'Toon oudere'.
# Bewaart daarnaast `dagen`: totalen per dag van de laatste 60 dagen (runs, nieuwe stukken van de laatste 14 dagen, aangevulde oudere stukken, verslagen) voor de hartslag op nieuw.html.
# Vergelijkt: officiële stukken (nieuw per soort, en moties/toezeggingen die afgedaan zijn), vergaderverslagen, komende vergaderingen.
import json,os,sys,datetime
import zstandard
from paden import DOCS,WERK

LOG=os.path.join(DOCS,'data','logboek.json'); ARCH=os.path.join(DOCS,'data','logboek'); VOOR=os.path.join(WERK,'logboek_voor.json')
IB='https://gemeenteraad.rotterdam.nl/Reports/Item/'

def lees(p,leeg):
    try: return json.load(open(p,encoding='utf8'))
    except (OSError,ValueError): return leeg

def stand():
    st={}
    try:
        d=json.loads(zstandard.ZstdDecompressor().stream_reader(open(os.path.join(DOCS,'data','ibabs','stukken.zst'),'rb')).read())
        S=d['soorten']
        for r in d['s']:
            k=r[7] or f'{r[0]}|{r[1]}|{r[2]}'
            st[k]=[S[r[0]],r[1],r[2],r[5] or '',r[7] if len(r[7] or '')==36 else '']
    except (OSError,ValueError,KeyError): pass
    verg={v['id']:[v['datum'],v['naam'],v.get('kort','')] for v in lees(os.path.join(DOCS,'verg','index.json'),[])}
    vo={}
    for v in lees(os.path.join(DOCS,'verg','vooruit.json'),{}).get('v',[]):
        vo[v.get('agendaId','')]=[v.get('datum',''),v.get('naam',''),len(v.get('punten',[]))]
    return {'stukken':st,'verg':verg,'vooruit':vo}

def afgedaan(s): s=s.lower(); return 'afgedaan' in s and 'niet afgedaan' not in s

def regel(oud,nu):
    nieuw=[v for k,v in nu['stukken'].items() if k not in oud['stukken']]
    af=[v for k,v in nu['stukken'].items() if k in oud['stukken'] and afgedaan(v[3]) and not afgedaan(oud['stukken'][k][3])]
    tel={}
    for v in nieuw: tel[v[0]]=tel.get(v[0],0)+1
    verg=[[k]+v for k,v in nu['verg'].items() if k not in oud['verg']]
    vo=[v for k,v in nu['vooruit'].items() if k not in oud['vooruit']]
    if not (nieuw or af or verg or vo): return None
    lijst=lambda xs:[{'soort':v[0],'datum':v[1],'titel':v[2],'link':IB+v[4] if v[4] else ''} for v in sorted(xs,key=lambda v:v[1],reverse=True)[:25]]
    vanaf=(datetime.date.today()-datetime.timedelta(days=14)).isoformat()
    return {'n_actueel':sum(1 for v in nieuw if v[1]>=vanaf),'nieuw_per_soort':dict(sorted(tel.items(),key=lambda x:-x[1])),'nieuw':lijst(nieuw),'n_nieuw':len(nieuw),
            'afgedaan':lijst(af),'n_afgedaan':len(af),
            'verslagen':[{'datum':d,'naam':n,'kort':k,'link':f'vergadering.html?id={i}'} for i,d,n,k in sorted(verg,key=lambda x:x[1],reverse=True)],
            'agenda':[{'datum':d,'naam':n,'punten':p} for d,n,p in sorted(vo)]}

def tel_dag(dagen,r):
    """Telt een run mee in de totalen van zijn dag. Oude regels zonder n_actueel: schatting uit de bewaarde stukken."""
    d=r['tijd'][:10]; e=dagen.setdefault(d,{'r':0,'n':0,'g':0,'v':0})
    act=r.get('n_actueel')
    if act is None:
        gr=(datetime.datetime.fromisoformat(r['tijd'])-datetime.timedelta(days=14)).date().isoformat()
        act=sum(1 for x in r['nieuw'] if x['datum']>=gr)
    e['r']+=1; e['n']+=act; e['g']+=max(0,r['n_nieuw']-act); e['v']+=len(r['verslagen'])

def archiveer(regels):
    os.makedirs(ARCH,exist_ok=True); per={}
    for x in regels: per.setdefault(x['tijd'][:7],[]).append(x)
    for m,xs in per.items():
        p=os.path.join(ARCH,m+'.json'); al=lees(p,{'regels':[]})['regels']; tijden={x['tijd'] for x in al}
        al=sorted(al+[x for x in xs if x['tijd'] not in tijden],key=lambda x:x['tijd'],reverse=True)
        json.dump({'regels':al},open(p,'w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
    maanden=sorted({f[:7] for f in os.listdir(ARCH) if len(f)==12 and f.endswith('.json')},reverse=True)
    json.dump({'maanden':maanden},open(os.path.join(ARCH,'index.json'),'w',encoding='utf8'))

def main():
    wat=sys.argv[1] if len(sys.argv)>1 else ''
    if wat=='voor':
        os.makedirs(WERK,exist_ok=True); json.dump(stand(),open(VOOR,'w',encoding='utf8'),ensure_ascii=False); return
    if wat!='na': sys.exit('gebruik: logboek.py voor|na')
    oud=lees(VOOR,None)
    if oud is None: print('geen voor-stand; niets gelogd'); return
    r=regel(oud,stand())
    if not r: print('niets nieuw'); return
    nu=datetime.datetime.now().astimezone()
    r={'tijd':nu.isoformat(timespec='minutes'),'modus':os.environ.get('RZ_MODUS',''),**r}
    L=lees(LOG,{'regels':[]})
    dagen=L.get('dagen')
    if dagen is None:
        dagen={}
        for x in L.get('regels',[]): tel_dag(dagen,x)
    tel_dag(dagen,r)
    dagen={d:v for d,v in dagen.items() if d>=(nu-datetime.timedelta(days=60)).date().isoformat()}
    R=[r]+L.get('regels',[])
    grens=(nu-datetime.timedelta(days=7)).isoformat()
    houd=[x for i,x in enumerate(R) if i<10 or x['tijd']>=grens]
    if len(houd)<len(R): archiveer(R[len(houd):])
    R=houd
    json.dump({'regels':R,'dagen':dagen},open(LOG,'w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
    print(f"gelogd: {r['n_nieuw']} nieuw, {r['n_afgedaan']} afgedaan, {len(r['verslagen'])} verslagen, {len(r['agenda'])} agenda")

if __name__=='__main__': main()
