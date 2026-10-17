# Uitgelichte citaten voor de startpagina: ca. 36 woordelijk gecontroleerde citaten uit de laatste 90 dagen,
# eerlijk verdeeld over fracties (om de beurt), buurcitaten steeds van een andere fractie.
#   python src/citaten_uit.py [dagen=90] [aantal=36]  -> docs/verg/citaten.json
import json,os,re,sys,datetime
from paden import DOCS
VD=os.path.join(DOCS,'verg')
PROC=re.compile(r'vaststelling van de agenda|opening|mededeling|rondvraag|insprek|sluiting|ingekomen stukken|^agenda$',re.I)  # gelijk aan index.html
def main(dagen=90,aantal=36):
    idx=json.load(open(os.path.join(VD,'index.json'),encoding='utf8'))
    nw=datetime.date.fromisoformat(idx[0]['datum']); grens=(nw-datetime.timedelta(days=dagen)).isoformat()
    per={}
    for m in idx:
        if m['datum']<grens or not m.get('n'): continue
        V=json.load(open(os.path.join(VD,m['id']+'.json'),encoding='utf8'))
        for a in V.get('agendapunten',[]):
            if PROC.search(a['titel']): continue
            for f in a.get('fracties',[]):
                c=f.get('citaat')
                if not(c and f.get('wie_bron') and f.get('sec') is not None and 60<=len(c)<=260 and re.match(r'[A-Z‘\'"]',c)): continue
                per.setdefault(f['wie'],[]).append({'t':c,'wie':f['wie_bron'],'fractie':f['wie'],'sec':f['sec'],'video':V.get('video'),'id8':m['id'],
                    'nr':a['nr'],'ap':a['titel'],'naam':V['naam'],'datum':V['datum'],'duur':a.get('duur') or 0})
    for l in per.values(): l.sort(key=lambda c:(-c['duur'],c['datum'],c['sec']))
    uit=[];gezien=set();i=0  # om de beurt per fractie (alfabet), niet twee keer hetzelfde agendapunt per ronde
    fr=sorted(per);rond=0
    while len(uit)<aantal and any(per.values()):
        for f in fr:
            if len(uit)>=aantal: break
            l=per[f]
            k=next((j for j,c in enumerate(l) if (c['id8'],c['nr'],f) not in gezien),None)
            if k is None: k=0 if (rond>2 and l) else None
            if k is None: continue
            c=l.pop(k);gezien.add((c['id8'],c['nr'],f));uit.append(c)
        rond+=1
        if rond>6: break
    json.dump({'stand':idx[0]['datum'],'c':uit},open(os.path.join(VD,'citaten.json'),'w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
    print(len(uit),'citaten,',len(per),'fracties')
if __name__=='__main__': main(*[int(x) for x in sys.argv[1:3]])
