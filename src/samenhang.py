# Samenhang van een onderwerp met andere onderwerpen, domeinen en gebieden (proef 5-10-2026, Parkeren).
#   python src/samenhang.py [slug]  -> docs/d/<slug>-samenhang.json
# Twee onderwerpen 'hangen samen' als ze in hetzelfde stuk tekst worden genoemd: binnen ca. 350 tekens van elkaar,
# in een debatbeurt (spreker x agendapunt) of in een officieel stuk. Telling = aantal beurten/stukken, niet aantal keren.
# Per verband één echt voorbeeld (fragment met bron), zodat je ziet waaróm ze samenhangen.
import json,os,re,sys,glob,collections
from paden import DOCS
from ontwerp_data import zload
from teksten import fold
import onderwerpen as OW, showcase as SC, themes
from dossier_data import slug as SLUG
VENSTER=350

def main(sl='parkeren'):
    CFG=SC.CONFIG[sl]; HOOFD=re.compile(r'\b(?:'+CFG['rx']+')')
    eigen={SLUG(n) for n,_ in OW.actief() if OW.THEMA.get(n)==CFG['naam']}|{sl}
    ANDER=[(SLUG(n),n,OW.rx(pp)) for n,pp in OW.actief() if SLUG(n) not in eigen]
    th=next(t for g in themes.T for t in g[1] if t[0]==CFG['naam']); SUB=[(n,SC.rx(t)) for n,t in th[2]]
    ix=json.load(open(os.path.join(DOCS,'d','index.json'),encoding='utf8'))['d']
    info={x['slug']:x for x in ix}
    dm=zload(os.path.join(DOCS,'data','debat','meta.zst')); tm=zload(os.path.join(DOCS,'data','tekst','meta.zst'))
    tel=collections.Counter(); jaar=collections.defaultdict(collections.Counter); vb={}; sub=collections.Counter(); subvb={}
    dom=collections.Counter(); geb=collections.Counter(); fr=collections.Counter(); totaal=collections.Counter()
    def vensters(t):
        f=fold(t); uit=[]
        for m in HOOFD.finditer(f):
            a,b=max(0,m.start()-VENSTER),m.end()+VENSTER
            if uit and a<=uit[-1][1]: uit[-1][1]=b
            else: uit.append([a,b])
        return f,[(a,b) for a,b in uit]
    def fragment(t,a,b,rx):
        m=rx.search(fold(t),a,b); h=HOOFD.search(fold(t),a,b)
        if not m or not h: return None
        lo,hi=min(m.start(),h.start()),max(m.end(),h.end())
        s,e=max(0,lo-110),min(len(t),hi+110)
        return ('…' if s else '')+re.sub(r'\s+',' ',t[s:e]).strip()+('…' if e<len(t) else ''),hi-lo
    def verwerk(t,y,bron,score):
        f,vv=vensters(t)
        if not vv: return False
        totaal[y]+=1
        gezien=set(); sgezien=set()
        for a,b in vv:
            for k,n,r in ANDER:
                if k in gezien or not r.search(f,a,b): continue
                gezien.add(k); tel[k]+=1; jaar[k][y]+=1
                fr_=fragment(t,a,b,r)
                if fr_ and len(fr_[0])<420 and (k not in vb or score-fr_[1]/60>vb[k][0]): vb[k]=(score-fr_[1]/60,dict(bron,fragment=fr_[0]))
            for n,r in SUB:
                if n in sgezien or not r.search(f,a,b): continue
                sgezien.add(n); sub[n]+=1
        return True
    # debatten
    B=dm['blok']; u=dm['u']; ap=dm['ap']; verg=dm['verg']
    for p in sorted(glob.glob(os.path.join(DOCS,'data','debat','b','*.zst'))):
        blk=zload(p); b0=int(os.path.basename(p)[:4])*B
        for j,segs in enumerate(blk):
            ui=b0+j; U=u[ui]; A=ap[U[0]]; V=verg[A[0]]
            t=' '.join(s for _,s in segs); y=V[0][:4]
            wie=dm['spk'][U[1]] if U[1]>=0 else ''
            if not wie or wie.lower().startswith('inspreker'): wie=''
            partij=dm['par'][U[2]] if U[2]>=0 else ''
            sec=next((s for s,x in segs if HOOFD.search(fold(x))),segs[0][0])
            bron={'soort':'debat','datum':V[0],'verg':V[2],'punt':A[2],'agenda':V[3],'video':V[4],'sec':sec,'wie':wie,'partij':partij}
            score=(V[0]>='2022')*10+(not U[4])*3+bool(partij)*2+bool(wie)+V[0][:4].isdigit()*int(V[0][:4])/10000
            if verwerk(t,y,bron,score):
                if A[3]>=0: dom[dm['dom'][A[3]][1]]+=1
                for g,n in enumerate(dm['geb']):
                    if A[4]>>g&1: geb[n]+=1
                if partij: fr[partij]+=1
    # officiële stukken
    D=tm['d']; BT=tm['blok']
    for p in sorted(glob.glob(os.path.join(DOCS,'data','tekst','b','*.zst'))):
        blk=zload(p); b0=int(os.path.basename(p).split('.')[0])*BT
        for j,t in enumerate(blk):
            if b0+j>=len(D) or not t: continue
            r=D[b0+j]; soort=tm['soorten'][r[0]]
            bron={'soort':soort,'datum':r[1],'titel':r[2],'url':r[4]}
            verwerk(r[2]+'. '+t,r[1][:4],bron,(r[1]>='2022')*10+int(r[1][:4] or 0)/10000)
    jaren=[str(j) for j in range(2018,2027)]
    rel=[]
    NM={k:n for k,n,_ in ANDER}
    for k in sorted(tel,key=lambda k:-tel[k]):
        n=NM[k]
        if tel[k]<8: continue
        x=info.get(k,{})
        rel.append({'slug':k,'naam':n,'domein':x.get('groep',''),'n':tel[k],'jaren':[jaar[k][j] for j in jaren],'ai':x.get('ai',False),
                    'termen':OW.termen(dict(OW.O)[n]).split('|')[0],'vb':vb.get(k,(0,None))[1]})
    pk=json.load(open(os.path.join(DOCS,'d',sl+'.json'),encoding='utf8'))
    uit={'slug':sl,'naam':CFG['naam'],'domein':info.get(sl,{}).get('groep',''),'stand':dm['stand'],'jaren':jaren,'totaal':[totaal[j] for j in jaren],'n':sum(totaal.values()),
         'verwant':rel,'sub':[[n,sub[n]] for n,_ in SUB],'domeinen':dom.most_common(),'gebieden':sorted(geb.items()),'fracties':sorted(fr.items()),
         'keten':{'moties':pk['moties'].get('aangenomen',0)+pk['moties'].get('verworpen',0),'toez':sum(pk['toez'].get(k,0) for k in('open','afgedaan')),'sv':pk['sv']['n']},
         'venster':VENSTER}
    json.dump(uit,open(os.path.join(DOCS,'d',sl+'-samenhang.json'),'w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
    print(uit['n'],'beurten/stukken;',[(r['naam'],r['n'],r['domein']) for r in rel[:20]]);print(uit['sub']);print(uit['domeinen'][:8])
if __name__=='__main__': main(*sys.argv[1:2])
