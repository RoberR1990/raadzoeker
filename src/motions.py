import re
Q="‘’'\"“”ꞌʺ„`´"
RES=re.compile(r"(De motie|Het amendement|Het subamendement|Het voorstel|Het initiatiefvoorstel|Het besluit|Het raadsvoorstel|Het ontwerpbesluit) is (met algemene stemmen|unaniem|zonder (?:hoofdelijke )?stemming|met (\d+) stem(?:men)? (voor|tegen) en (\d+) (?:stem(?:men)? )?(voor|tegen)|met (\d+) (?:stemmen )?tegen (\d+)|[^.]{0,60}?)\s*(aangenomen|verworpen|aanvaard|aangehouden|ingetrokken)")
HEAD=re.compile(r"(Motie|Amendement|Subamendement)\s+([0-9A-Z]{1,4}[a-zA-Z]?)\s*[,.:]?\s*(?:over\s*:?\s*)?["+Q+r"]{0,2}\s*([^"+Q+r"\n]{3,220}?)\s*["+Q+r"]{0,2}\s*[.,]?\s*(?:U kunt stemmen\.?\s*|Stemmen maar\.?\s*|De stemming is geopend\.?\s*)?$")
FR=re.compile(r"\s*(Voor|Tegen) (?:hebben gestemd|stemden|heeft gestemd|stemde|waren|was) (?:de |het )?(?:fracties?|leden|lid)?\s*(?:van )?([^.]{2,400})\.")
def find(text):
    out=[]
    for m in RES.finditer(text):
        kind=m.group(1)
        pre=text[max(0,m.start()-330):m.start()]
        # take last sentence-ish chunk containing Motie/Amendement
        h=None
        for hm in re.finditer(r"(Motie|Amendement|Subamendement)\s+[0-9A-Z]{1,4}[a-zA-Z]?\b",pre): h=hm
        nr='';title='';typ={'De motie':'Motie','Het amendement':'Amendement','Het subamendement':'Subamendement'}.get(kind,'Voorstel')
        if h and typ!='Voorstel':
            hh=HEAD.search(pre[h.start():])
            if hh: typ,nr,title=hh.group(1),hh.group(2),hh.group(3).strip()
            else:
                seg=pre[h.start():]; mm=re.match(r"(Motie|Amendement|Subamendement)\s+([0-9A-Z]{1,4}[a-zA-Z]?)\s*[,.:]?\s*(.*)$",seg,re.S)
                typ,nr,title=mm.group(1),mm.group(2),re.sub(r"\s+"," ",mm.group(3)).strip(" .,"+Q)[:200]
        elif typ=='Voorstel':
            mm=re.search(r"(?:Besluit over|Raadsvoorstel|Het voorstel(?: tot| met betrekking tot)?)\s*,?\s*([^\n]{5,220})$",pre.split('\n')[-1])
            title=mm.group(1).strip(" .,"+Q) if mm else ''
            if not title: continue
        if typ!='Voorstel' and not nr: continue
        res=m.group(9); res={'aanvaard':'aangenomen'}.get(res,res)
        v=t=-1
        if m.group(3):
            a,sa,b,sb=int(m.group(3)),m.group(4),int(m.group(5)),m.group(6)
            if sa==sb: sb='tegen' if sa=='voor' else 'voor'
            v,t=(a,b) if sa=='voor' else (b,a)
        elif m.group(7): v,t=int(m.group(7)),int(m.group(8)); 
        side='';fr=''
        f=FR.match(text[m.end():m.end()+500].lstrip('. '))
        if f: side=f.group(1).lower(); fr=re.sub(r"\s+"," ",f.group(2)).strip()
        out.append({'typ':typ,'nr':nr,'title':re.sub(r"\s+"," ",title).strip(' ,.'+Q),'res':res,'voor':v,'tegen':t,'side':side,'fr':fr,'pos':m.start()})
    return out
