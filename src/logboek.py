# Logboek 'Wat is er nieuw' -> docs/data/logboek.json (pagina docs/nieuw.html, link achter 'bijgewerkt' in de kop).
#   python src/logboek.py voor   vóór de run: legt de huidige stand vast in WERK/logboek_voor.json
#   python src/logboek.py na     na de run: vergelijkt, en voegt alleen bij verschil een regel toe
# Bewaart de regels van de laatste 3 dagen, maximaal 50, maar altijd minstens de laatste 10.
# Vergelijkt: officiële stukken (nieuw per soort, en moties/toezeggingen die afgedaan zijn), vergaderverslagen, komende vergaderingen.
import json,os,sys,datetime
import zstandard
from paden import DOCS,WERK

LOG=os.path.join(DOCS,'data','logboek.json'); VOOR=os.path.join(WERK,'logboek_voor.json')
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
    return {'nieuw_per_soort':dict(sorted(tel.items(),key=lambda x:-x[1])),'nieuw':lijst(nieuw),'n_nieuw':len(nieuw),
            'afgedaan':lijst(af),'n_afgedaan':len(af),
            'verslagen':[{'datum':d,'naam':n,'kort':k,'link':f'vergadering.html?id={i}'} for i,d,n,k in sorted(verg,key=lambda x:x[1],reverse=True)],
            'agenda':[{'datum':d,'naam':n,'punten':p} for d,n,p in sorted(vo)]}

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
    L=lees(LOG,{'regels':[]}); R=[r]+L.get('regels',[])
    grens=(nu-datetime.timedelta(days=3)).isoformat()
    R=[x for i,x in enumerate(R) if i<10 or x['tijd']>=grens][:50]
    json.dump({'regels':R},open(LOG,'w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
    print(f"gelogd: {r['n_nieuw']} nieuw, {r['n_afgedaan']} afgedaan, {len(r['verslagen'])} verslagen, {len(r['agenda'])} agenda")

if __name__=='__main__': main()
