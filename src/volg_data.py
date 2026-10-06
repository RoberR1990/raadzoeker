# Volgen: per dossier (domein, onderwerp, thema, gebied) de nieuwste items van de laatste 60 dagen, voor 'nieuw sinds je vorige bezoek'
# en voor pushmeldingen.  python src/volg_data.py  -> docs/ontwerp/volg.json  (draait op de NAS na dossier_data en verg_koppel)
# Item: [datum, soort, titel, link]; soort: vergadering | motie | toezegging | vragen | debat.
import json,os,glob,datetime
from paden import DOCS
D=os.path.join(DOCS,'ontwerp')
def main(dagen=60,maxn=12):
    vanaf=(datetime.date.today()-datetime.timedelta(days=dagen)).isoformat()
    K=json.load(open(os.path.join(D,'verg','koppel.json'),encoding='utf8')) if os.path.exists(os.path.join(D,'verg','koppel.json')) else {}
    IX={x['slug']:x for x in json.load(open(os.path.join(D,'d','index.json'),encoding='utf8'))['d']}
    uit={}
    for slug,x in IX.items():
        if x['soort']=='kruising': continue
        p=os.path.join(D,'d',slug+'.json')
        if not os.path.exists(p): continue
        d=json.load(open(p,encoding='utf8')); it=[]
        for v in K.get(slug,[]):   # [id8, nr, titel, datum, naam]
            it.append([v[3],'vergadering',f'{v[4]}: {v[2]}',f'vergadering.html?id={v[0]}#ap-{v[1]}'])
        gezien={(i[0],i[2].split(': ',1)[-1].lower()) for i in it}
        for veld,soort in (('moties','motie'),('toez','toezegging'),('sv','vragen')):
            for r in (d.get(veld) or {}).get('lijst',[]):
                if r and r[0]>=vanaf: it.append([r[0],soort,r[1],r[4] if len(r)>4 else ''])
        for r in d.get('debatten',[]):   # [datum, agendaId, agendapunt, …] — alleen als er geen samenvatting van die vergadering is
            if r[0]>=vanaf and not any(i[0]==r[0] and i[1]=='vergadering' for i in it):
                it.append([r[0],'debat',r[2],f'https://gemeenteraad.rotterdam.nl/Agenda/Index/{r[1]}'])
        it=[i for i in it if i[0]>=vanaf]
        if not it: continue
        it.sort(key=lambda i:i[0],reverse=True)
        uit[slug]={'naam':x['naam'],'soort':x['soort'],'i':it[:maxn]}
    out={'stand':datetime.date.today().isoformat(),'d':uit}
    json.dump(out,open(os.path.join(D,'volg.json'),'w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
    print('volg.json',len(uit),'dossiers met nieuws,',os.path.getsize(os.path.join(D,'volg.json'))//1024,'kB')
if __name__=='__main__': main()
