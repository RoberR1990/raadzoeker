import re
P=re.compile(r"(zeg(?:gen)? (?:ik|wij|we) (?:(?:u|jullie|de raad|hierbij|graag|dat|het|dit|ook|dan|bij dezen?|nu|wel|zeker|allemaal|hem|haar|ze|die|u dat|u ook) ){0,3}toe\b|(?:kan|wil|zal|ga|kunnen|willen|zullen) (?:ik|wij|we) (?:[\w'’-]+ ){0,5}?toezeggen|\b(?:ik|wij|we) (?:kan|wil|zal|kunnen|willen|zullen) (?:[\w'’-]+ ){0,5}?toezeggen|toezegging (?:doe|kan|wil) ik|\bik zeg (?:(?:u|dat|het|hierbij|graag|dit) ){0,2}toe\b|doe ik (?:(?:u|graag|hierbij|die|deze|de|een|bij dezen?) ){0,3}toezegging|die toezegging (?:doe|kan|wil) ik|\bbij dezen? toegezegd|\bdat is toegezegd\b)",re.I)
P2=re.compile(r"(schriftelijk (?:op |bij u |bij de raad )?(?:op )?terug|schriftelijk (?:te )?(?:informeren|beantwoorden|doen toekomen|laten weten|afdoen)|(?:brief|raadsbrief|raadsinformatiebrief) (?:naar|aan) (?:u|uw raad|de raad|de commissie) (?:[\w'-]+ ){0,3}?(?:sturen|toesturen|doen toekomen)|informeer ik (?:u|uw raad|de raad)|zal ik (?:u|uw raad|de raad) (?:[\w'-]+ ){0,3}?informeren)",re.I)
NEG=re.compile(r"\b(niet|geen|nooit)\b",re.I)
def find(text,pat=P):
    out=[]; last=-1
    for m in pat.finditer(text):
        if NEG.search(m.group(0)): continue
        # sentence bounds: previous sentence + this one
        a=m.start()
        s1=max(text.rfind('. ',0,a),text.rfind('? ',0,a),text.rfind('! ',0,a),text.rfind('\n',0,a))
        s0=max(text.rfind('. ',0,max(0,s1)),text.rfind('? ',0,max(0,s1)),text.rfind('! ',0,max(0,s1)),text.rfind('\n',0,max(0,s1))) if s1>0 else -1
        start=(s0+2 if s0>=0 and text[s0]!='\n' else s0+1) if s1>0 and s1-s0<350 else (s1+2 if s1>=0 and text[s1]!='\n' else s1+1)
        start=max(0,start)
        e=m.end(); ends=[x for x in (text.find('. ',e),text.find('? ',e),text.find('! ',e),text.find('\n',e)) if x>=0]
        end=min(ends)+1 if ends else len(text)
        if end-start>700: start=max(start,a-300); end=min(end,e+300)
        if start<=last: 
            out[-1][1]=max(out[-1][1],end); continue
        out.append([start,end]); last=end
    return out
