# Verrassende verbanden, stap 3 (zonder AI): mechanische controle van de redactionele keuze en publicatie.
#   python src/verrassend_check.py  -> docs/ontwerp/verrassend.json
# Invoer: data/verrassend/keuze.json (per paar knoop-id's a/b, uitleg, toelichting, citaat met broncode, extra broncodes 'ook').
# Broncode D<n> = beurt n in de debat-index, S<n> = stuk n in de tekst-index (zelfde codes als verrassend_in.py).
# Geschrapt wordt: een paar waarvan een knoop niet (meer) in verkenner.json staat, of waarvan het citaat niet woordelijk
# (op witruimte na) in de bron staat. Een extra bron vervalt als niet beide begrippen erin staan.
# Spreker alleen als fractie of 'college/voorzitter', geen namen; insprekers komen niet voor (al uitgesloten in stap 1).
import json,os,re,sys
from paden import DOCS,DATA
from ontwerp_data import zload
import teksten as T

def ws(s): return re.sub(r'\s+',' ',s).strip()

class Bron:
    def __init__(self):
        self.dm=zload(os.path.join(DOCS,'data','debat','meta.zst')); self.tm=zload(os.path.join(DOCS,'data','tekst','meta.zst')); self.blk={}
    def _blok(self,soort,n):
        k=(soort,n)
        if k not in self.blk:
            p=os.path.join(DOCS,'data','debat','b',f'{n:04d}.zst') if soort=='D' else os.path.join(DOCS,'data','tekst','b',f'{n:03d}.zst')
            self.blk[k]=zload(p)
        return self.blk[k]
    def get(self,code):
        """(tekst, metadata) van een broncode"""
        s,i=code[0],int(code[1:])
        if s=='D':
            B=self.dm['blok']; segs=self._blok('D',i//B)[i%B]; U=self.dm['u'][i]; A=self.dm['ap'][U[0]]; V=self.dm['verg'][A[0]]
            t=ws(' '.join(x[1] for x in segs))
            meta={'code':code,'soort':'debat','datum':V[0],'titel':ws(A[2] or V[2])[:160],'verg':V[2],
                  'wie':self.dm['par'][U[2]] if U[2]>=0 else 'college of voorzitter',
                  'url':f'https://gemeenteraad.rotterdam.nl/Agenda/Index/{V[3]}' if V[3] else ''}
        else:
            B=self.tm['blok']; r=self.tm['d'][i]; t=ws(r[2]+'. '+(self._blok('S',i//B)[i%B] or ''))
            meta={'code':code,'soort':self.tm['soorten'][r[0]].lower() if r[0]<len(self.tm['soorten']) else 'stuk','datum':r[1],'titel':ws(r[2])[:160],'url':r[4] or ''}
        return t,meta

def heeft(t,k):
    """staat de woordstam k (knoop-id zonder 'w:') in tekst t"""
    return any(T.stam(T.fold(w))==k for w in re.findall(r'[^\W\d_]+',t))

def main():
    K=json.load(open(os.path.join(DOCS,'ontwerp','verkenner.json'),encoding='utf8'))
    idx={k['id']:i for i,k in enumerate(K['knopen'])}; dom=K['dom']
    keuze=json.load(open(os.path.join(DATA,'verrassend','keuze.json'),encoding='utf8'))
    B=Bron(); uit=[]; weg=0
    for c in keuze:
        if c['a'] not in idx or c['b'] not in idx: print('knoop ontbreekt:',c['a'],c['b']); weg+=1; continue
        t,meta=B.get(c['code'])
        if ws(c['citaat']) not in t: print('citaat niet gevonden:',c['code'],c['citaat'][:60]); weg+=1; continue
        ook=[]
        for code in c.get('ook',[]):
            t2,m2=B.get(code)
            if all(heeft(t2,x[2:]) for x in (c['a'],c['b'])): ook.append(m2)
            else: print('extra bron zonder beide begrippen:',code)
        A,Bk=K['knopen'][idx[c['a']]],K['knopen'][idx[c['b']]]
        uit.append({'a':c['a'],'b':c['b'],'la':A['l'],'lb':Bk['l'],'da':dom[A['dom']][1],'db':dom[Bk['dom']][1],
                    'uitleg':c['uitleg'],'toelichting':c['toelichting'],'citaat':ws(c['citaat']),'bron':meta,'ook':ook})
    json.dump({'stand':K['stand'],'paren':uit},open(os.path.join(DOCS,'ontwerp','verrassend.json'),'w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
    print(len(uit),'paren gepubliceerd,',weg,'geschrapt')
    return 0 if uit else 1
if __name__=='__main__': sys.exit(main())
