# Echte data voor de promovideo -> video/src/data.json.  python video/data.py
import json,os,sys
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,os.path.join(R,'src'))
import teksten as T
from ontwerp_data import zload
O=os.path.join(R,'docs','ontwerp'); DB=os.path.join(R,'docs','data','debat')
L=lambda p:json.load(open(os.path.join(O,p),encoding='utf8'))
ov=L('d/overzicht.json'); pk=L('d/parkeren.json'); px=L('d/parkeren-extra.json'); ps=L('samenvattingen/parkeren.json')
dh=L('d/delfshaven.json'); ds=L('samenvattingen/delfshaven.json'); ka=L('kaart.json'); wk=L('wijken.json')
meta=zload(os.path.join(DB,'meta.zst')); tm=zload(os.path.join(R,'docs','data','tekst','meta.zst'))
def treffers(q):   # aantal debatbeurten waarin alle woorden voorkomen (zelfde index als zoek.html)
    s=None
    for w in T.woorden(q):
        sh=zload(os.path.join(DB,'i',f'{T.h(w):03d}.zst')); p=sh.get(w)
        b=set(); x=0
        for d in (p[0] if p else []): x+=d; b.add(x)
        s=b if s is None else s&b
    return len(s or [])
wolk=sorted(ov['wolk'],key=lambda x:-x[4])[:44]
deb=[d for d in px['debatten'] if d.get('fragment') and d.get('sec') and 'parkeer' in d['fragment'].lower() and d['wie'] and not d['wie'].startswith('Inspreker')][:3]
mot=[r for r in px['stemmen']['tabel'] if 'parkeer' in r[1].lower()][:1]
spoor=[s for s in px['spoor'] if s.get('stappen')][:4]
DH=[w for w in wk['wijken'] if w['gebied']=='Delfshaven']
uit={
 'stand':ov['stand'],
 'wolk':[[x[0],x[4]] for x in wolk],
 'totaal':{'beurten':len(meta['u']),'stukken':len(tm['d']),'vergaderingen':len(meta['verg'])},
 'zoek':{'q':'parkeren','n':treffers('parkeren'),'jaren':pk['jaren'],'per':pk['trendn'],
   'hits':[{'datum':d['datum'],'verg':d['verg'],'punt':d['punt'],'wie':d['wie'],'partij':d.get('partij',''),'fragment':d['fragment'].strip('…'),'sec':d['sec']} for d in deb]},
 'breed':[[q,treffers(q)] for q in ['jeugdzorg','woningbouw','haven','overlast','armoede','tramlijn']],
 'domeinen':[[d['naam'],[d['kruising'].get(g,0) for g in ov['gebieden']]] for d in ov['domeinen']],'gebieden':ov['gebieden'],
 'parkeren':{'kern':[{k:z.get(k) for k in('zin','citaat','bron_label','bron_datum')} for z in ps['kern']],
   'akkoord':px['akkoord']['passages'][:3],
   'spoor':[{k:s.get(k) for k in('soort','datum','titel','wie','open','stappen','toezegging')} for s in spoor],
   'motie':mot[0] if mot else None,'moties':pk['moties'],'toez':{k:pk['toez'][k] for k in('open','te_laat','afgedaan')}},
 'kaart':{'w':ka['w'],'h':ka['h'],'gebieden':[[g['naam'],g['d']] for g in ka['gebieden']],'water':ka['water'],'havens':ka['havens']},
 'delfshaven':{'kern':[{k:z.get(k) for k in('zin','citaat','bron_label','bron_datum')} for z in ds['kern']],
   'jaren':dh['jaren'],'per':dh['trendn'],
   'domeinen':sorted([[d['naam'],d['kruising'].get('Delfshaven',0)] for d in ov['domeinen']],key=lambda x:-x[1]),
   'wijken':[{'naam':w['naam'],'d':w['d'],'lx':w['lx'],'ly':w['ly'],'inw':w['cbs'].get('2024',{}).get('inw'),'woz':w['cbs'].get('2024',{}).get('woz'),'huur':w['cbs'].get('2024',{}).get('huur')} for w in DH],
   'wijkraad':[s[:2] for s in dh['wijkstukken'][:4]],
   'moties':{k:dh['moties'][k] for k in('aangenomen','open','afgedaan')},'sv':dh['sv']['n']},
}
json.dump(uit,open(os.path.join(R,'video','src','data.json'),'w',encoding='utf8'),ensure_ascii=False,indent=1)
print(uit['totaal'],uit['zoek']['n'],uit['breed'],len(DH),'wijken',uit['parkeren']['motie'] and uit['parkeren']['motie'][1])
