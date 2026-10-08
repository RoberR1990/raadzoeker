# Vooruitblik: komende vergaderingen van raad en commissies (iBabs-kalender), met per agendapunt de dossiers en
# wanneer het onderwerp eerder op de agenda stond (tijdlijn uit de iBabs-stukken, zoals verg_koppel.spoor).
#   python src/vooruit.py [dagen=21]  -> docs/verg/vooruit.json
import json,os,re,sys,html,datetime
import ibabs, verg_koppel as K
from wijkraad_verg import lees
from paden import DOCS
B='https://gemeenteraad.rotterdam.nl'
MND={m:i+1 for i,m in enumerate('januari februari maart april mei juni juli augustus september oktober november december'.split())}
SKIP=re.compile(r'procedurevergadering|presidium|agendacommissie|werkgeverscommissie|auditcommissie|seniorenconvent|fractievoorzitters|besloten',re.I)
PROC=re.compile(r'^(opening|sluiting|mededeling|vaststell(ing|en) (van )?(de )?(agenda|notulen|besluitenlijst)|ingekomen|rondvraag|vragenuur|lijst van|actualiteit|toezeggingen|termijnagenda|adviezenlijst|insprek|inspreker|overlegvergadering|betrekken bij|moties en toezeggingen|technische sessie$)',re.I)
def main(dagen=21):
    van=datetime.date.today(); tot=van+datetime.timedelta(days=dagen); verg={}
    for d in {van,tot,van+datetime.timedelta(days=dagen//2)}:
        h=ibabs.get(B+f'/Calendar/GetMonthAgendas?month={d.month-1}&year={d.year}',cache=False)
        for aid,tid,lab,dag in re.findall(r'href="/Agenda/Index/([0-9a-f-]+)"[^>]*data-agendatype-id="(\d+)"[^>]*>\s*<div class="calendar-item-label">\s*([^<]+?)\s*(?:<span.*?)?</div>\s*<div class="sr-only">\s*\w+ (\d+ \w+ \d{4})',h,re.S):
            g,m,j=dag.split(); dt=datetime.date(int(j),MND[m],int(g))
            if van<=dt<=tot and not SKIP.search(lab): verg[aid]=(dt.isoformat(),html.unescape(lab).strip())
    I=K.ibabs(); from ontwerp_data import zload
    m=zload(os.path.join(DOCS,'data','debat','meta.zst')); VERG={(v[0],K.orgnorm(v[2])):v[3] for v in m['verg'] if v[3]}
    import glob; GEDAAN={os.path.basename(p)[:8] for p in glob.glob(os.path.join(K.VD,'*.json'))}
    uit=[]; Z=json.load(open(os.path.join(K.VD,'zoek.json'),encoding='utf8'))
    for aid,(datum,naam) in sorted(verg.items(),key=lambda x:x[1]):
        _,_,items=lees(ibabs.get(B+f'/Agenda/Index/{aid}',cache=False))
        V={'datum':datum,'naam':naam,'raad':naam.startswith('Gemeenteraad')}
        punten=[]
        for it in items:
            nr=it['nr'].strip('.').lstrip('0'); t=it['titel'].strip()
            if not t or PROC.search(t) or 'inspreek' in t.lower() or (not V['raad'] and nr.startswith('1')): continue
            a={'nr':nr,'titel_off':t}
            sp=K.spoor(V,a,I,VERG,GEDAAN)
            eerder=[x for x in sp['tl'] if x[0]<datum]
            # ook eerdere samengevatte vergaderingen met een (bijna) gelijke titel, ook zonder gedeeld iBabs-stuk
            ws=K.woordset(t)
            for z in Z:
                ov=ws&K.woordset(z[2]+' '+z[6][:200])
                if z[3]<datum and ws and (len(ov)/len(ws)>=.5 or any(len(w)>=8 for w in ov)) and not any(e[4]==z[0] for e in eerder):
                    eerder.append([z[3],z[4],z[1],z[2],z[0],'',0])
            eerder.sort()
            punten.append({'nr':nr,'titel':t,'dossiers':K.dossiers(t,it.get('tekst','')[:600],None,0)[:3],'eerder':eerder[-4:],'st':len(sp['st'])})
        if punten or V['raad']: uit.append({'agendaId':aid,'datum':datum,'naam':naam,'punten':punten})
        print(datum,naam,len(punten),'punten',flush=True)
    json.dump({'gemaakt':van.isoformat(),'v':uit},open(os.path.join(K.VD,'vooruit.json'),'w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
if __name__=='__main__': main(int(sys.argv[1]) if len(sys.argv)>1 else 21)
