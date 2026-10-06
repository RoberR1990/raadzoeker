# Citaatcontrole voor vergadersamenvattingen en publicatie.
#   python src/verg_check.py <agendaId> [uitvoer.json]  -> docs/ontwerp/verg/<id8>.json (+ index.json)
# Een zin/punt blijft alleen staan als het citaat letterlijk in de genoemde beurt (#U) staat (volledige tekst, niet het ingekorte
# pakket) en, bij fracties, als die beurt van die fractie is; bij het college als de spreker die naam draagt.
# Per citaat de seconde in de video (begin van het segment waarin het citaat begint).
import json,os,re,sys,unicodedata
from paden import DOCS,WERK
def n(s): return re.sub(r'\s+',' ',''.join(c for c in unicodedata.normalize('NFD',s.lower()) if unicodedata.category(c)!='Mn').replace('’',"'").replace('‘',"'").replace('“','"').replace('”','"')).strip().strip('.…"\' ')
def main(ag,pad=None):
    k=ag[:8]; B=json.load(open(os.path.join(WERK,'verg',f'bron_{k}.json'),encoding='utf8'))
    d=json.load(open(pad or os.path.join(WERK,'verg',f'uit_{k}.json'),encoding='utf8'))
    weg=[]
    def ok(x,soort):
        u=B['u'].get(str(x.get('u','')).lstrip('#U').lstrip('U'))
        q=n(x.get('citaat',''))
        if not u or len(q.split())<5: return False
        segs=u['segs']; heel=n(' '.join(s for _,s in segs))
        if q not in heel: return False
        if soort=='fractie' and n(x.get('wie',''))!=n(u['par']): return False
        if soort=='college' and not any(w in n(u['wie']) for w in n(x.get('wie','')).split() if len(w)>3): return False
        # seconde: segment waarin het citaat begint
        acc='';sec=segs[0][0]
        for s,t in segs:
            if n(acc+' '+t).find(q[:40])>=0: sec=s; break
            acc+=' '+t
        x['sec']=max(0,int(sec)); x['wie_bron']=u['wie']; return True
    kort=[z for z in d.get('kort',[]) if ok(z,'kort')]; weg+=[('kort',z.get('zin','')[:50]) for z in d.get('kort',[]) if z not in kort]
    for a in d.get('agendapunten',[]):
        for veld,soort in (('fracties','fractie'),('college','college'),('toezeggingen','tz')):
            oud=a.get(veld,[]); a[veld]=[x for x in oud if ok(x,soort)]; weg+=[(a.get('nr'),veld,x.get('wie',x.get('wat',''))[:40]) for x in oud if x not in a[veld]]
    V=B['verg']; woorden=lambda t:len(t.split())
    wk=sum(woorden(z['zin']) for z in kort)
    wu=sum(woorden(a.get('wat',''))+woorden(a.get('uitkomst',''))+sum(woorden(x.get('punt',x.get('wat',''))) for v in ('fracties','college','toezeggingen') for x in a[v]) for a in d['agendapunten'])
    out={'agendaId':ag,'datum':V[0],'naam':V[2],'raad':V[1]==0,'video':V[4],'kort':kort,'agendapunten':d['agendapunten'],
         'leestijd':{'kort':max(1,round(wk/200)),'uitgebreid':max(1,round((wu+wk)/200))},'gemaakt':d.get('model','Claude Sonnet'),'geschrapt':len(weg)}
    os.makedirs(os.path.join(DOCS,'ontwerp','verg'),exist_ok=True)
    json.dump(out,open(os.path.join(DOCS,'ontwerp','verg',f'{k}.json'),'w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
    ix=os.path.join(DOCS,'ontwerp','verg','index.json'); L=json.load(open(ix,encoding='utf8')) if os.path.exists(ix) else []
    L=[x for x in L if x['id']!=k]+[{'id':k,'agendaId':ag,'datum':V[0],'naam':V[2],'raad':V[1]==0,'kort':kort[0]['zin'] if kort else '','n':len(out['agendapunten'])}]
    json.dump(sorted(L,key=lambda x:(x['datum'],x['naam']),reverse=True),open(ix,'w',encoding='utf8'),ensure_ascii=False,indent=0)
    print(k,'kort',len(kort),'punten',len(out['agendapunten']),'leestijd',out['leestijd'],'geschrapt',len(weg)); [print('  -',w) for w in weg[:15]]
if __name__=='__main__': main(*sys.argv[1:3])
