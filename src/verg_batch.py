# Terugwerkend samenvatten: welke vergaderingen nog moeten, nieuwste eerst, met zuinige invoerpakketten.
#   python src/verg_batch.py lijst [vanaf=JJJJ-MM-DD] [n]   -> maakt de pakketten (verg_in --zuinig) en print agendaId + woorden
#   python src/verg_batch.py check                           -> verg_check voor elk uit_<id8>.json dat nog niet gepubliceerd is
# Het samenvatten zelf doen Sonnet-subagents met src/verg_prompt.md (in: WERK/verg/in_<id8>.txt, uit: WERK/verg/uit_<id8>.json).
import os,sys,glob,io,contextlib
from paden import DOCS,WERK
from ontwerp_data import zload
import verg_in,verg_check
VD=os.path.join(DOCS,'verg'); WD=os.path.join(WERK,'verg')
def gedaan(): return {os.path.basename(p)[:8] for p in glob.glob(os.path.join(VD,'*.json'))}
def lijst(vanaf,n):
    m=zload(os.path.join(DOCS,'data','debat','meta.zst'))
    w={}
    for u in m['u']: w[m['ap'][u[0]][0]]=w.get(m['ap'][u[0]][0],0)+u[3]
    G=gedaan(); L=[(v[0],v[3],v[2]) for i,v in enumerate(m['verg']) if v[0]>=vanaf and v[3] and w.get(i,0)>2000 and v[3][:8] not in G]
    L.sort(reverse=True); tot=0
    for d,ag,naam in L[:n]:
        p=os.path.join(WD,f'in_{ag[:8]}.txt')
        if not os.path.exists(p):
            with contextlib.redirect_stdout(io.StringIO()): verg_in.main(ag,2200)
        k=len(open(p,encoding='utf8').read().split()); tot+=k
        print(d,ag,k,naam)
    print('totaal',len(L[:n]),'vergaderingen',tot,'woorden', 'van',len(L),'nog te doen')
def check():
    G=gedaan()
    for p in sorted(glob.glob(os.path.join(WD,'uit_*.json'))):
        k=os.path.basename(p)[4:12]
        if len(os.path.basename(p))!=17 or k in G: continue
        ag=open(os.path.join(WD,f'in_{k}.txt'),encoding='utf8').readline().split('agendaId ')[1].split(' |')[0]
        try: verg_check.main(ag)
        except Exception as e: print(k,'FOUT',e)
if __name__=='__main__':
    if sys.argv[1]=='lijst': lijst(sys.argv[2] if len(sys.argv)>2 else '2024-10-06',int(sys.argv[3]) if len(sys.argv)>3 else 9999)
    else: check()
