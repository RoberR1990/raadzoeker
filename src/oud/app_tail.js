/* ---------- thema's: vaste zoeksets (termen gescheiden door | ; "x" = heel woord) ---------- */
const THEMES=[
 ['Beleidsdomeinen',[
  ['Parkeren','parkeer | parkeren'],
  ['Mobiliteit & verkeer','verkeer | mobiliteit | fiets | openbaar vervoer | "metro" | "tram" | deelscooter | deelvervoer'],
  ['Wonen','woning | huurder | woonvisie | corporatie | daklo | leegstand'],
  ['Bouwen & ruimte','bestemmingsplan | omgevingsvisie | omgevingswet | omgevingsplan | gebiedsontwikkeling | stedenbouw | hoogbouw'],
  ['Buitenruimte & afval','afval | container | buitenruimte | zwerfvuil | grofvuil | riolering | bomenkap | groenonderhoud'],
  ['Energie & klimaat','klimaat | energie | warmtenet | aardgas | duurzaam | co2 | stikstof | luchtkwaliteit'],
  ['Veiligheid & handhaving','veiligheid | handhav | politie | cameratoezicht | explosie | fouilleren | overlast | ondermijning'],
  ['Werk & inkomen','bijstand | armoede | schulden | participatiewet | werkloos | bestaanszekerheid | minimabeleid'],
  ['Zorg, welzijn & jeugd','jeugdzorg | wmo | welzijn | mantelzorg | ouderen | "ggd" | eenzaamheid | huisarts'],
  ['Onderwijs','onderwijs | school | scholen | leerling | leraren | kinderopvang'],
  ['Economie & haven','haven | ondernemer | economie | horeca | werkgelegenheid | winkel | "mkb"'],
  ['Cultuur, sport & evenementen','cultuur | museum | "sport" | sportverenig | sportpark | evenement | festival | bibliothe'],
  ['Financiën & belastingen','begroting | jaarstukken | "ozb" | belasting | bezuinig | voorjaarsnota | weerstandsvermogen'],
  ['Asiel & migratie','asiel | statushouder | vluchteling | opvanglocatie | spreidingswet | arbeidsmigrant | "coa"'],
  ['Dienstverlening & organisatie','dienstverlening | 14010 | stadswinkel | ambtenar | inhuur | reorganisatie | bedrijfsvoering']]],
 ['Thema’s dwars door de organisatie',[
  ['AI & algoritmen','"ai" | kunstmatige intelligentie | artificial intelligence | algoritme | chatgpt | generatieve | machine learning | taalmodel'],
  ['Data & privacy','privacy | "avg" | persoonsgegevens | datalek | gegevensbescherming | datagedreven | open data | dataset'],
  ['Digitalisering & ICT','digitalis | digitale | "ict" | cyber | software | glasvezel | smart city'],
  ['Participatie & inspraak','participatie | inspraak | wijkraad | wijkraden | referendum | burgerberaad | bewonersinitiatief'],
  ['Discriminatie & inclusie','discriminatie | racisme | inclusie | diversiteit | emancipatie | lhbt | toegankelijkheid'],
  ['Integriteit & transparantie','integriteit | geheimhouding | "woo" | transparant | klokkenluider | belangenverstrengeling'],
  ['Inkoop, aanbesteding & subsidie','aanbested | inkoop | subsidie | leverancier | contractmanagement'],
  ['Onderzoek & verantwoording','rekenkamer | evaluatie | monitor | ombudsman | "audit" | accountant'],
  ['Innovatie & experimenten','innovatie | "pilot" | experiment | proeftuin | start-up'],
  ['Regio & Rijk','metropoolregio | "mrdh" | provincie | rijksoverheid | "vng" | kabinet'],
  ['Toezeggingen','zeg ik toe | zeg ik u toe | toezegging | kan ik toezeggen | zeggen wij toe']]]];
const PALIAS={'Partij voor de Dieren':['partij voor de dieren','pvdd'],'ChristenUnie-SGP':['christenunie','cu-sgp'],'Leefbaar Rotterdam':['leefbaar'],'Forum voor Democratie':['forum voor democratie','fvd'],'50PLUS':['50plus','50+']};

/* ---------- toestand ---------- */
const F=['q','q2','fs','fp','fr','fd1','fd2','fa','fk'];
let VIEW='t', MRES='', wantSort='new';
function state(){const s={};for(const f of F)s[f]=$(f).value.trim();s.ww=$('ww').checked;s.sort=wantSort;s.view=VIEW;s.mres=MRES;return s;}
function active(s){return !!(s.q||s.q2||s.fs||s.fp||s.fr||s.fd1||s.fd2||s.fa||s.fk!=='01');}
function toHash(s){const p=new URLSearchParams();for(const f of F)if(s[f]&&!(f==='fk'&&s[f]==='01'))p.set(f,s[f]);if(s.ww)p.set('ww','1');if(s.sort!=='new')p.set('sort',s.sort);if(VIEW!=='t')p.set('v',VIEW);if(MRES)p.set('mres',MRES);const h=p.toString();history.replaceState(null,'',h?'#'+h:location.pathname+location.search);}
function fromHash(){const p=new URLSearchParams(location.hash.slice(1));for(const f of F)if(p.has(f))$(f).value=p.get(f);$('ww').checked=p.get('ww')==='1';VIEW=p.get('v')==='m'?'m':'t';MRES=p.get('mres')||'';wantSort=p.get('sort')||'new';}
function parseTerms(q,ww){return q.split('|').map(x=>x.trim()).filter(Boolean).map(x=>{const m=/^"(.+)"$/.exec(x);const t=normQ(m?m[1]:x);return {t,w:!!m||ww,label:m?m[1]:x};}).filter(x=>x.t);}

/* ---------- zoeken ---------- */
function isW(c){return (c>=97&&c<=122)||(c>=48&&c<=57);}
function search(s){
  let terms=parseTerms(s.q,s.ww),t2=parseTerms(s.q2,s.ww);
  if(!terms.length){terms=t2;t2=[];}
  const fsn=normQ(s.fs);let spSet=null;
  if(fsn){spSet=new Set();SPK.forEach((x,i)=>{if(norm(x[0]).includes(fsn))spSet.add(i);});}
  const pIdx=s.fp?PAR.indexOf(s.fp):-2, fa=normQ(s.fa), kinds=s.fk, role=s.fr, hasQ=terms.length>0;
  const rOK=r=>{switch(role){case'':return true;case'raad':return r===0;case'college':return r===2||r===3;case'wethouder':return r===2;case'burgemeester':return r===3;case'voorzitter':return r===1;case'nietvz':return r!==1;default:return r>=4;}};
  const res=[];let hits=0;const ty=terms.map(()=>({})),wy={},wp={},tot=terms.map(()=>0);
  for(const D of Y){
    const S=D.s,n=S.t.length,N=D.N,off=D.off;
    const mOK=D.M.map(m=>(!s.fd1||m[0]>=s.fd1)&&(!s.fd2||m[0]<=s.fd2));
    if(!mOK.some(Boolean))continue;
    const iOK=fa?D.In.map(x=>x.includes(fa)):null;
    const ok=i=>{const k=S.k[i];
      if(k===3){if(hasQ||!kinds.includes('0'))return false;}else if(k===4){if(!kinds.includes('0'))return false;}else if(!kinds.includes(String(k)))return false;
      if(!mOK[S.m[i]])return false;if(iOK&&!iOK[S.i[i]])return false;
      if(spSet&&!spSet.has(S.sp[i]))return false;if(pIdx!==-2&&S.pa[i]!==pIdx)return false;
      if(role&&(S.sp[i]<0||!rOK(S.ro[i])))return false;
      if((spSet||pIdx!==-2)&&S.sp[i]<0)return false;return true;};
    const okc=new Int8Array(n);let wsum=0;
    for(let i=0;i<n;i++){if(ok(i)){okc[i]=1;wsum+=D.w[i];const p=S.pa[i];if(p>=0)wp[p]=(wp[p]||0)+D.w[i];}}
    wy[D.y]=wsum;
    if(hasQ){
      const cnt=new Int32Array(n);
      if(t2.length){for(let i=0;i<n;i++){if(!okc[i])continue;let f=false;for(const x of t2){const p=N.indexOf(x.t,off[i]);if(p>=0&&p<off[i+1]){f=true;break;}}if(!f)okc[i]=0;}}
      terms.forEach((tm,ti)=>{let pos=0,seg=0,c=0;const q=tm.t,ql=q.length;
        while((pos=N.indexOf(q,pos))!==-1){
          if(tm.w&&((pos>0&&isW(N.charCodeAt(pos-1)))||isW(N.charCodeAt(pos+ql)))){pos++;continue;}
          while(off[seg+1]<=pos)seg++;
          if(okc[seg]){cnt[seg]++;c++;}
          pos+=ql;}
        ty[ti][D.y]=c;tot[ti]+=c;hits+=c;});
      for(let i=0;i<n;i++)if(cnt[i])res.push({D,i,c:cnt[i]});
    }else{for(let i=0;i<n;i++)if(okc[i])res.push({D,i,c:0});}
  }
  return {res,hits,terms,t2,ty,tot,wy,wp,q:hasQ};
}
function sortRes(R,how){
  const d=o=>o.D.M[o.D.s.m[o.i]][0];
  if(how==='old')R.res.sort((a,b)=>d(a)<d(b)?-1:d(a)>d(b)?1:a.i-b.i);
  else if(how==='hits'&&R.q)R.res.sort((a,b)=>b.c-a.c||(d(a)<d(b)?1:d(a)>d(b)?-1:a.i-b.i));
  else R.res.sort((a,b)=>d(a)<d(b)?1:d(a)>d(b)?-1:a.i-b.i);
}

/* ---------- weergave ---------- */
function ranges(text,terms){
  const nt=norm(text),r=[];
  for(const tm of terms){if(!tm||!tm.t)continue;const t=tm.t;let p=0;while((p=nt.indexOf(t,p))!==-1){if(tm.w&&((p>0&&isW(nt.charCodeAt(p-1)))||isW(nt.charCodeAt(p+t.length)))){p++;continue;}r.push([p,p+t.length]);p+=t.length;}}
  r.sort((a,b)=>a[0]-b[0]);const o=[];for(const x of r){if(o.length&&x[0]<=o[o.length-1][1])o[o.length-1][1]=Math.max(o[o.length-1][1],x[1]);else o.push(x);}
  return o;
}
const allTerms=()=>RES&&RES.q?RES.terms.concat(RES.t2):[];
function markup(text,rs,from,to){
  let h='',p=from;
  for(const [a,b] of rs){if(b<=from||a>=to)continue;const a2=Math.max(a,from),b2=Math.min(b,to);h+=esc(text.slice(p,a2))+'<mark>'+esc(text.slice(a2,b2))+'</mark>';p=b2;}
  return h+esc(text.slice(p,to));
}
function paras(text,rs){let h='',p=0;for(const part of text.split('\n')){h+='<p>'+markup(text,rs,p,p+part.length)+'</p>';p+=part.length+1;}return h;}
function snipRanges(text,rs){
  if(!rs.length){const cut=text.length>340?text.lastIndexOf(' ',340):text.length;return [[0,cut>0?cut:Math.min(340,text.length)]];}
  const W=170,wins=[];
  for(const [a,b] of rs){if(wins.length&&a-wins[wins.length-1][1]<W){wins[wins.length-1][1]=Math.min(text.length,b+W);continue;}if(wins.length>=3)break;wins.push([Math.max(0,a-W),Math.min(text.length,b+W)]);}
  return wins.map(w=>{let a=w[0],b=w[1];if(a>0){const s=text.indexOf(' ',a);if(s>0&&s<a+30)a=s+1;}if(b<text.length){const s=text.lastIndexOf(' ',b);if(s>b-30)b=s;}return [a,b];});
}
function snippets(text,rs){
  return snipRanges(text,rs).map(([a,b])=>'<p>'+(a>0?'<span class="more">… </span>':'')+markup(text,rs,a,b).replace(/\n/g,' ')+(b<text.length?'<span class="more"> …</span>':'')+'</p>').join('');
}
function who(D,i){
  const S=D.s,k=S.k[i];
  if(S.sp[i]<0)return {name:KIND[k]||'Tekst in notulen',party:'',role:''};
  return {name:SPK[S.sp[i]][0],party:S.pa[i]>=0?PAR[S.pa[i]]:'',role:ROLES[S.ro[i]]};
}
function links(D,i){
  const S=D.s,m=D.M[S.m[i]],o=[];
  if(m[1])o.push([(S.v[i]>=0?'▶ video vanaf '+hms(S.v[i]):'Vergadering')+' (iBabs)',SRC+'/Agenda/Index/'+m[1]]);
  if(S.d[i]>=0){const d=D.D[S.d[i]];o.push(['Notulen (pdf)'+(S.pg[i]?' · p. '+S.pg[i]:''),SRC+'/Agenda/Document/'+d[1]+'?documentId='+d[0]+(d[2]?'&agendaItemId='+d[2]:'')]);}
  return o;
}
function itemLabel(D,it){const x=D.I[it];return (x[1]?x[1]+' ':'')+(x[2]||'(voor het eerste agendapunt)');}
function cardHTML(o,idx){
  const D=o.D,i=o.i,S=D.s,m=D.M[S.m[i]],w=who(D,i),k=S.k[i],text=S.t[i];
  const rs=ranges(text,allTerms()),il=itemLabel(D,S.i[i]);
  let h='<article class="card" data-r="'+idx+'"><div class="meta"><span class="date">'+fdate(m[0])+'</span>'+(S.z[i]?'<span>'+ZIT[S.z[i]]+'</span>':'')+
    '<span class="item"><a data-act="read" title="Lees het hele debat bij dit agendapunt">'+esc(il.slice(0,170))+(il.length>170?'…':'')+'</a></span></div>';
  h+='<div class="who"><b>'+esc(w.name)+'</b>'+(w.party?'<span class="tag party">'+esc(w.party)+'</span>':'')+(w.role&&w.role!=='raadslid'?'<span class="tag">'+w.role+'</span>':'')+
     (k===3?'<span class="tag warn">nog geen notulen · sprak om '+hms(S.pg[i])+'</span>':'')+(k===4?'<span class="tag warn">automatische ondertiteling · controleer in de video</span>':'')+(o.c>1?'<span class="tag">'+o.c+'× in deze tekst</span>':'')+'</div>';
  if(k!==3)h+='<div class="snip">'+snippets(text,rs)+'</div>';
  h+='<div class="acts">';
  if(k!==3){h+='<button class="btn small" data-act="full" type="button">Hele tekst</button><button class="btn small" data-act="read" type="button">Debat lezen</button><button class="btn small primary" data-act="copy" type="button">Kopieer citaat</button>';}
  else h+='<button class="btn small" data-act="read" type="button">Sprekerslijst agendapunt</button>';
  h+='<span class="src">'+links(D,i).map(l=>'<a href="'+l[1]+'" target="_blank" rel="noopener">'+esc(l[0])+' ↗</a>').join('')+'</span></div></article>';
  return h;
}
function citation(D,i,sel){
  const S=D.s,m=D.M[S.m[i]],w=who(D,i),it=D.I[S.i[i]],k=S.k[i];
  const text=(sel||S.t[i]).replace(/\s*\n\s*/g,' ').trim();
  let by;
  if(S.sp[i]<0)by=k===4?'Uitzending':'Notulen ('+w.name.toLowerCase()+')';
  else{const x=[];if(w.role&&w.role!=='raadslid'&&w.role!=='overig')x.push(w.role);if(w.party)x.push(w.party);by=w.name+(x.length?' ('+x.join(', ')+')':'');}
  const l=links(D,i),url=m[1]?SRC+'/Agenda/Index/'+m[1]:'';
  let c='“'+text+'”\n— '+by+', raadsvergadering Rotterdam '+fdate(m[0],true)+(it[1]?', agendapunt '+it[1]:'')+(it[2]?' ‘'+it[2].replace(/\.$/,'')+'’':'')+
    (k===4?', automatische ondertiteling van de uitzending (niet het officiële verslag), vanaf '+hms(S.v[i]):(S.pg[i]&&S.d[i]>=0?', notulen p. '+S.pg[i]:'')+(S.v[i]>=0?', video ca. '+hms(S.v[i]):''))+'.';
  if(url)c+='\nBron: '+url;
  if(S.d[i]>=0)c+='\nNotulen (pdf): '+l[l.length-1][1];
  return c;
}
function copy(txt,msg){
  const done=()=>toast(msg||'Citaat met bron gekopieerd');
  const fb=()=>{const t=document.createElement('textarea');t.value=txt;t.style.position='fixed';t.style.opacity='0';document.body.appendChild(t);t.select();try{document.execCommand('copy');done();}catch(e){toast('Kopiëren lukt niet in deze browser');}t.remove();};
  if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(txt).then(done,fb);else fb();
}
let tt;function toast(m){const t=$('toast');t.textContent=m;t.classList.add('on');clearTimeout(tt);tt=setTimeout(()=>t.classList.remove('on'),1800);}
function selIn(el){const s=window.getSelection();if(!s||s.isCollapsed||!s.rangeCount)return '';const r=s.getRangeAt(0);return el.contains(r.commonAncestorContainer)?s.toString().trim():'';}
function download(name,rows){
  const csv='﻿'+rows.map(r=>r.map(v=>{v=String(v==null?'':v).replace(/\s*\n\s*/g,' ');return /[";\n]/.test(v)?'"'+v.replace(/"/g,'""')+'"':v;}).join(';')).join('\r\n');
  const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));a.download=name;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(a.href),5000);
}
function tabsHTML(){return '<div class="tabs" role="tablist"><button type="button" role="tab" data-view="t" class="'+(VIEW==='t'?'on':'')+'">Teksten</button><button type="button" role="tab" data-view="m" class="'+(VIEW==='m'?'on':'')+'">Moties &amp; stemmingen</button></div>';}

function trendHTML(R){
  const ys=META.years.map(y=>+y.y).sort(),Wd=560,Hh=170,L=38,Rr=10,Tt=10,B=24,x=i=>L+(Wd-L-Rr)*(ys.length>1?i/(ys.length-1):.5);
  let series=[];
  if(R.q){
    const order=R.terms.map((t,i)=>i).sort((a,b)=>R.tot[b]-R.tot[a]).slice(0,5);
    series=order.map((ti,k)=>({name:R.terms[ti].label,cls:'s'+(k+1),abs:ys.map(y=>R.ty[ti][y]||0)}));
    if(R.terms.length>1)series.unshift({name:'alle termen samen',cls:'s0',abs:ys.map(y=>R.terms.reduce((a,t,ti)=>a+(R.ty[ti][y]||0),0))});
    series.forEach(sr=>sr.v=sr.abs.map((a,i)=>R.wy[ys[i]]>20000?a/R.wy[ys[i]]*1e5:null));
  }else{const c={};for(const o of R.res)c[o.D.y]=(c[o.D.y]||0)+1;series=[{name:'aantal teksten',cls:'s1',abs:ys.map(y=>c[y]||0)}];series[0].v=series[0].abs.slice();}
  const mx=Math.max(1e-9,...series.flatMap(s=>s.v.filter(v=>v!=null))),y=v=>Tt+(Hh-Tt-B)*(1-v/mx);
  const tick=mx>=10?Math.round(mx):Math.round(mx*10)/10;
  let g='<svg viewBox="0 0 '+Wd+' '+Hh+'" role="img" aria-label="Trend per jaar"><line class="ax" x1="'+L+'" y1="'+y(0)+'" x2="'+(Wd-Rr)+'" y2="'+y(0)+'"/><line class="gr" x1="'+L+'" y1="'+y(mx)+'" x2="'+(Wd-Rr)+'" y2="'+y(mx)+'"/><text class="tk" x="'+(L-5)+'" y="'+(y(mx)+4)+'" text-anchor="end">'+String(tick).replace('.',',')+'</text><text class="tk" x="'+(L-5)+'" y="'+(y(0)+4)+'" text-anchor="end">0</text>';
  ys.forEach((yy,i)=>{g+='<g class="yr" data-year="'+yy+'"><rect x="'+(x(i)-26)+'" y="0" width="52" height="'+Hh+'" fill="transparent"/><text class="tk" x="'+x(i)+'" y="'+(Hh-6)+'" text-anchor="middle">'+yy+'</text></g>';});
  series.slice().reverse().forEach(sr=>{const pts=sr.v.map((v,i)=>v==null?null:[x(i),y(v)]);let d='',pen=false;pts.forEach(p=>{if(!p){pen=false;return;}d+=(pen?'L':'M')+p[0].toFixed(1)+' '+p[1].toFixed(1);pen=true;});
    g+='<path class="ln '+sr.cls+'" d="'+d+'"/>';pts.forEach((p,i)=>{if(p)g+='<circle class="pt '+sr.cls+'" cx="'+p[0].toFixed(1)+'" cy="'+p[1].toFixed(1)+'" r="3"><title>'+esc(sr.name)+' · '+ys[i]+': '+sr.abs[i]+(R.q?' treffers ('+sr.v[i].toFixed(1).replace('.',',')+' per 100.000 woorden)':' teksten')+'</title></circle>';});});
  g+='</svg>';
  return '<div class="chart wide"><h3>'+(R.q?'Trend · treffers per 100.000 gesproken woorden':'Trend · aantal teksten per jaar')+' · klik op een jaar om te filteren</h3>'+g+'<div class="legend">'+series.map(sr=>'<span><i class="'+sr.cls+'"></i>'+esc(sr.name)+' <b>'+nf(sr.abs.reduce((a,b)=>a+b,0))+'</b></span>').join('')+'</div></div>';
}
function renderResults(s){
  const R=RES,res=R.res,out=$('out');
  const perP={},perS={},meet=new Set();
  for(const o of res){const S=o.D.s,v=R.q?o.c:1;const p=S.pa[o.i];if(p>=0)perP[p]=(perP[p]||0)+v;const sp=S.sp[o.i];if(sp>=0&&S.ro[o.i]!==1)perS[sp]=(perS[sp]||0)+v;meet.add(o.D.y+'-'+S.m[o.i]);}
  let h=tabsHTML()+'<div class="summary"><div class="n"><b>'+nf(res.length)+'</b> '+(res.length===1?'tekst':'teksten')+(R.q?' met <b>'+nf(R.hits)+'</b> '+(R.hits===1?'treffer':'treffers'):'')+' in '+meet.size+' '+(meet.size===1?'vergadering':'vergaderingen')+'</div>'+
    '<button class="btn small" id="csv" type="button" style="margin-left:auto">Exporteer (CSV)</button><select id="sort" aria-label="Sortering"><option value="new">Nieuwste eerst</option><option value="old">Oudste eerst</option>'+(R.q?'<option value="hits">Meeste treffers eerst</option>':'')+'</select></div>';
  if(Y.length<META.years.length)h+='<p class="hint">Nog niet alle jaren zijn geladen; de lijst vult zich aan.</p>';
  if(res.length){
    h+=trendHTML(R)+'<div class="charts">';
    const unit=R.q?'treffers':'teksten';
    const pv=p=>R.q&&R.wp[p]>20000?perP[p]/R.wp[p]*1e5:null;
    const ps=Object.keys(perP).map(Number).sort((a,b)=>R.q?((pv(b)||0)-(pv(a)||0)):perP[b]-perP[a]).filter(p=>!R.q||pv(p)!=null).slice(0,8),pm=Math.max(1e-9,...ps.map(p=>R.q?pv(p):perP[p]));
    h+='<div class="chart"><h3>'+(R.q?'Wie heeft het erover · per 100.000 woorden van de fractie':'Per partij')+'</h3><div class="hbars">'+(ps.length?ps.map(p=>'<button type="button" data-party="'+esc(PAR[p])+'" title="'+nf(perP[p])+' '+unit+'"><span class="t">'+esc(PAR[p])+'</span><span class="b" style="width:'+Math.max(2,Math.round(100*(R.q?pv(p):perP[p])/pm))+'%"></span><span class="v">'+(R.q?pv(p).toFixed(1).replace('.',',')+' <small>('+nf(perP[p])+')</small>':nf(perP[p]))+'</span></button>').join(''):'<span class="sub">Geen partijgebonden sprekers in deze selectie.</span>')+'</div></div>';
    const ss=Object.keys(perS).map(Number).sort((a,b)=>perS[b]-perS[a]).slice(0,8),sm=Math.max(1,...ss.map(p=>perS[p]));
    h+='<div class="chart"><h3>Sprekers · aantal '+unit+' (zonder voorzitter)</h3><div class="hbars">'+(ss.length?ss.map(p=>'<button type="button" data-spk="'+esc(SPK[p][0])+'"><span class="t">'+esc(SPK[p][0])+'</span><span class="b" style="width:'+Math.max(2,Math.round(100*perS[p]/sm))+'%"></span><span class="v">'+nf(perS[p])+'</span></button>').join(''):'<span class="sub">Geen sprekers in deze selectie.</span>')+'</div></div></div>';
  }
  if(R.q){
    const ag=[];for(const D of Y){D.In.forEach((x,it)=>{const m=D.M[D.I[it][0]];if(R.terms.some(t=>x.includes(t.t))&&(!s.fd1||m[0]>=s.fd1)&&(!s.fd2||m[0]<=s.fd2))ag.push({D,it,d:m[0]});});}
    ag.sort((a,b)=>a.d<b.d?1:-1);
    if(ag.length){h+='<details class="agd"'+(ag.length<=6?' open':'')+'><summary>Agendapunten met de zoekterm in de titel ('+ag.length+')</summary><div class="agl">'+ag.slice(0,40).map(a=>'<div><span class="date">'+fdate(a.d)+'</span><a data-item="'+a.D.y+':'+a.it+'">'+esc(itemLabel(a.D,a.it).slice(0,200))+'</a>'+(a.D.M[a.D.I[a.it][0]][3]===1?'':'<span class="tag warn">geen notulen</span>')+'</div>').join('')+(ag.length>40?'<div class="sub">… en '+(ag.length-40)+' meer; verfijn met het filter Agendapunt.</div>':'')+'</div></details>';}
  }
  if(!res.length)h+='<div class="empty">Niets gevonden. De zoekterm wordt letterlijk gezocht: probeer een korter stuk tekst, zet “hele woorden” uit of verruim de filters. Meerdere termen scheid je met | (of).</div>';
  h+=res.slice(0,shown).map((o,k)=>cardHTML(o,k)).join('');
  if(res.length>shown)h+='<div class="more-row"><button class="btn primary" id="more" type="button">Toon meer ('+nf(res.length-shown)+' resterend)</button></div>';
  out.innerHTML=h;
  $('sort').value=(wantSort==='hits'&&!R.q)?'new':wantSort;
}
/* moties & stemmingen */
let MO=null;
function motionList(s){
  const terms=parseTerms(s.q||s.q2,false),fa=normQ(s.fa);
  const al=s.fp?(PALIAS[s.fp]||[norm(s.fp)]):null,out=[];
  for(const D of Y){D.mo.forEach((m,k)=>{const S=D.s,mt=D.M[S.m[m[0]]];
    if((s.fd1&&mt[0]<s.fd1)||(s.fd2&&mt[0]>s.fd2))return;
    if(MRES&&String(m[4])!==MRES)return;
    if(terms.length&&!terms.some(t=>D.moN[k].includes(t.t)))return;
    if(fa&&!D.In[S.i[m[0]]].includes(fa))return;
    if(al){const f=norm(m[8]);if(!al.some(a=>f.includes(a)))return;}
    out.push({D,m,d:mt[0]});});}
  out.sort((a,b)=>wantSort==='old'?(a.d<b.d?-1:a.d>b.d?1:a.m[0]-b.m[0]):(a.d<b.d?1:a.d>b.d?-1:a.m[0]-b.m[0]));
  return out;
}
const MT={M:'Motie',A:'Amendement',S:'Subamendement',V:'Voorstel'};
function renderMotions(s){
  MO=motionList(s);const terms=parseTerms(s.q||s.q2,false);
  const aan=MO.filter(o=>o.m[4]).length;
  let h=tabsHTML()+'<div class="summary"><div class="n"><b>'+nf(MO.length)+'</b> stemmingen · <b>'+nf(aan)+'</b> aangenomen · <b>'+nf(MO.length-aan)+'</b> verworpen</div>'+
   '<select id="mres" aria-label="Uitkomst" style="margin-left:auto"><option value="">Alle uitkomsten</option><option value="1">Aangenomen</option><option value="0">Verworpen</option></select><button class="btn small" id="csv" type="button">Exporteer (CSV)</button><select id="sort" aria-label="Sortering"><option value="new">Nieuwste eerst</option><option value="old">Oudste eerst</option></select></div>'+
   '<p class="hint">Uit de stemuitslagen in de notulen gehaald (moties, amendementen en voorstellen waarover is gestemd). De zoekterm zoekt hier in de titel; het partijfilter kijkt of de fractie bij de genoemde voor- of tegenstemmers staat. De notulen noemen meestal alleen de minderheid. Spreker- en rolfilter gelden hier niet.</p>';
  if(!MO.length)h+='<div class="empty">Geen stemmingen gevonden met deze zoekterm en filters.</div>';
  h+='<div class="mol">'+MO.slice(0,shown*2).map((o,k)=>{const m=o.m,t=m[3];
    return '<div class="mo" data-mo="'+k+'"><span class="date">'+fdate(o.d)+'</span><span class="res '+(m[4]?'ja':'nee')+'">'+(m[4]?'aangenomen':'verworpen')+(m[5]>=0?' '+m[5]+'–'+m[6]:(m[4]?' · algemene stemmen':''))+'</span><a class="ti" data-act="mread"><span class="ty">'+MT[m[1]]+(m[2]?' '+esc(m[2]):'')+'</span> '+markup(t,ranges(t,terms),0,t.length)+'</a>'+(m[8]?'<span class="fr">'+(m[7]==='v'?'Voor':'Tegen')+': '+esc(m[8])+'</span>':'')+'</div>';}).join('')+'</div>';
  if(MO.length>shown*2)h+='<div class="more-row"><button class="btn primary" id="more" type="button">Toon meer ('+nf(MO.length-shown*2)+' resterend)</button></div>';
  $('out').innerHTML=h;$('mres').value=MRES;$('sort').value=wantSort==='old'?'old':'new';
}
function exportCSV(){
  const stamp=META.built;
  if(VIEW==='m'){const rows=[['datum','soort','nummer','titel','uitkomst','voor','tegen','genoemde fracties','agendapunt','bron']];
    for(const o of MO){const m=o.m,S=o.D.s,mt=o.D.M[S.m[m[0]]];rows.push([o.d,MT[m[1]],m[2],m[3],m[4]?'aangenomen':'verworpen',m[5]>=0?m[5]:'',m[6]>=0?m[6]:'',(m[8]?(m[7]==='v'?'voor: ':'tegen: ')+m[8]:''),itemLabel(o.D,S.i[m[0]]),mt[1]?SRC+'/Agenda/Index/'+mt[1]:'']);}
    download('raadzoeker-stemmingen-'+stamp+'.csv',rows);return;}
  const rows=[['datum','agendapunt','spreker','partij','rol','soort','treffers','fragment','notulenpagina','videotijd','bron','notulen pdf']],tm=allTerms();
  for(const o of RES.res.slice(0,20000)){const D=o.D,i=o.i,S=D.s,m=D.M[S.m[i]],w=who(D,i),k=S.k[i],text=S.t[i],l=links(D,i);
    const fr=snipRanges(text,ranges(text,tm)).map(([a,b])=>text.slice(a,b)).join(' … ');
    rows.push([m[0],itemLabel(D,S.i[i]),S.sp[i]>=0?w.name:'',w.party,w.role,k===0?'spreekbeurt (notulen)':k===1?'motie/stemming (notulen)':k===2?'presentielijst':k===3?'sprekerstijdlijn':'automatische ondertiteling',o.c||'',fr,S.d[i]>=0&&S.pg[i]?S.pg[i]:'',S.v[i]>=0?hms(S.v[i]):'',m[1]?SRC+'/Agenda/Index/'+m[1]:'',S.d[i]>=0?l[l.length-1][1]:'']);}
  download('raadzoeker-treffers-'+stamp+'.csv',rows);
  if(RES.res.length>20000)toast('Eerste 20.000 rijen geëxporteerd');
}
function renderBrowse(){
  let h=tabsHTML()+'<p class="hint">Typ een zoekterm (meerdere termen met | ertussen), kies een thema of blader door de vergaderingen en open een agendapunt om het debat te lezen.</p>';
  h+='<div class="themes">'+THEMES.map(g=>'<div class="tg"><h3>'+g[0]+'</h3><div class="chips">'+g[1].map(t=>'<button type="button" class="chip" data-theme="'+esc(t[1])+'" title="'+esc(t[1])+'">'+esc(t[0])+'</button>').join('')+'</div></div>').join('')+'</div>';
  h+='<h2 class="sec">Vergaderingen</h2>';
  Y.forEach((D,k)=>{
    const ms=D.M.map((m,i)=>i).sort((a,b)=>D.M[a][0]<D.M[b][0]?1:-1);
    h+='<details class="yr"'+(k===0?' open':'')+'><summary>'+D.y+' <small>'+D.M.length+' vergaderingen · '+nf(D.nSp)+' spreekbeurten</small></summary>';
    for(const mi of ms){const m=D.M[mi];
      h+='<details class="mt" data-m="'+D.y+':'+mi+'"><summary><span class="date">'+fdate(m[0])+'</span>'+(m[2]&&m[2]!=='Gemeenteraad'?'<span>'+esc(m[2])+'</span>':'')+
        (m[3]===1?'<span class="sub">'+nf(D.mc[mi])+' spreekbeurten</span>':m[3]===2?'<span class="tag warn">nog geen notulen · automatische ondertiteling</span>':'<span class="tag warn">nog geen notulen · sprekerstijdlijn</span>')+'</summary></details>';}
    h+='</details>';
  });
  if(!Y.length)h+='<div class="empty">Bezig met laden…</div>';
  $('out').innerHTML=h;
}
function fillMeeting(el){
  if(el.dataset.done)return;el.dataset.done=1;
  const [y,mi]=el.dataset.m.split(':').map(Number),D=Y.find(d=>d.y===y);
  let h='<ol>';D.I.forEach((it,k)=>{if(it[0]!==mi)return;h+='<li><span class="nr">'+esc(it[1])+'</span><a data-item="'+y+':'+k+'">'+esc(it[2]||'(voor het eerste agendapunt)')+'</a><span class="c">'+(D.ic[k]||'–')+'</span></li>';});
  h+='</ol>';el.insertAdjacentHTML('beforeend',h);
}

/* ---------- lezer ---------- */
let RD=null;
function openReader(D,it,focus){
  RD={D,it};const S=D.s,x=D.I[it],m=D.M[x[0]];
  $('rmeta').textContent=fdate(m[0],false)+(m[2]&&m[2]!=='Gemeenteraad'?' · '+m[2]:'')+(m[3]===1?'':m[3]===2?' · nog geen notulen: tekst is automatische ondertiteling van de uitzending':' · nog geen notulen, alleen sprekerstijdlijn');
  $('rtitle').textContent=itemLabel(D,it);
  const terms=allTerms();let h='',first=D.first[it];
  if(first<0)h='<div class="empty">Bij dit agendapunt zijn geen sprekers of teksten vastgelegd.</div>';
  else{
    $('rlinks').innerHTML=links(D,first).map(l=>'<a href="'+l[1]+'" target="_blank" rel="noopener">'+esc(l[0])+' ↗</a>').join('');
    for(let i=first;i<S.t.length&&S.i[i]===it;i++){
      const w=who(D,i),k=S.k[i],text=S.t[i];
      h+='<div class="sp'+(k===1||k===2?' doc':'')+(S.ro[i]===1&&k===0?' chair':'')+(i===focus?' focus':'')+'" data-i="'+i+'"><div class="h"><b>'+esc(w.name)+'</b>'+(w.party?'<span class="tag party">'+esc(w.party)+'</span>':'')+(w.role&&w.role!=='raadslid'?'<span class="tag">'+w.role+'</span>':'')+
        (k===3?'<span class="tag warn">'+hms(S.pg[i])+'</span>':'<span class="sub">'+(k!==4&&S.pg[i]?'p. '+S.pg[i]:'')+(S.v[i]>=0?(k!==4&&S.pg[i]?' · ':'')+'▶ '+hms(S.v[i]):'')+'</span><button class="btn small cp" data-act="rcopy" type="button">Kopieer citaat</button>')+'</div>'+
        (k===3?'':paras(text,ranges(text,terms)))+'</div>';
    }
  }
  if(first<0)$('rlinks').innerHTML=m[1]?'<a href="'+SRC+'/Agenda/Index/'+m[1]+'" target="_blank" rel="noopener">Vergadering (iBabs) ↗</a>':'';
  $('rbody').innerHTML=h;$('reader').classList.add('on');document.body.style.overflow='hidden';
  const f=$('rbody').querySelector('.focus');$('rbody').scrollTop=0;if(f)f.scrollIntoView({block:'start'});
  const same=k=>k>=0&&k<D.I.length&&D.I[k][0]===x[0];
  $('rprev').disabled=!same(it-1);$('rnext').disabled=!same(it+1);
}
function closeReader(){$('reader').classList.remove('on');document.body.style.overflow='';RD=null;}

/* ---------- regie ---------- */
let deb;
function update(fromLoad){
  const s=state();
  const key=JSON.stringify(s)+Y.length;
  if(key===lastKey)return;
  if(!fromLoad){shown=PAGE;toHash(s);}
  lastKey=key;
  if(VIEW==='m'){RES=null;renderMotions(s);return;}
  if(!active(s)){RES=null;renderBrowse();return;}
  RES=search(s);sortRes(RES,s.sort);renderResults(s);
}
function schedule(){clearTimeout(deb);deb=setTimeout(()=>update(false),180);}
for(const f of F){$(f).addEventListener('input',schedule);$(f).addEventListener('change',schedule);}
$('ww').addEventListener('change',schedule);
$('theme').addEventListener('change',e=>{if(e.target.value){$('q').value=e.target.value;e.target.value='';VIEW='t';update(false);}});
$('reset').addEventListener('click',()=>{for(const f of F)$(f).value=f==='fk'?'01':'';$('ww').checked=false;wantSort='new';MRES='';update(false);$('q').focus();});
$('out').addEventListener('change',e=>{if(e.target.id==='sort'){wantSort=e.target.value;update(false);}if(e.target.id==='mres'){MRES=e.target.value;update(false);}});
$('out').addEventListener('toggle',e=>{if(e.target.classList&&e.target.classList.contains('mt')&&e.target.open)fillMeeting(e.target);},true);
$('out').addEventListener('click',e=>{
  const t=e.target.closest('[data-act],[data-year],[data-party],[data-spk],[data-item],[data-theme],[data-view],#more,#csv');if(!t)return;
  if(t.id==='more'){shown+=PAGE*2;VIEW==='m'?renderMotions(state()):renderResults(state());return;}
  if(t.id==='csv'){exportCSV();return;}
  if(t.dataset.view){VIEW=t.dataset.view;update(false);return;}
  if(t.dataset.theme){$('q').value=t.dataset.theme;VIEW='t';update(false);window.scrollTo(0,0);return;}
  if(t.dataset.year){const y=t.dataset.year,on=$('fd1').value===y+'-01-01'&&$('fd2').value===y+'-12-31';$('fd1').value=on?'':y+'-01-01';$('fd2').value=on?'':y+'-12-31';update(false);return;}
  if(t.dataset.party){$('fp').value=$('fp').value===t.dataset.party?'':t.dataset.party;update(false);return;}
  if(t.dataset.spk){$('fs').value=$('fs').value===t.dataset.spk?'':t.dataset.spk;update(false);return;}
  if(t.dataset.item){const [y,it]=t.dataset.item.split(':').map(Number);openReader(Y.find(d=>d.y===y),it,-1);return;}
  if(t.dataset.act==='mread'){const o=MO[+t.closest('.mo').dataset.mo];openReader(o.D,o.D.s.i[o.m[0]],o.m[0]);return;}
  const card=t.closest('.card');if(!card)return;const o=RES.res[+card.dataset.r];
  if(t.dataset.act==='read')openReader(o.D,o.D.s.i[o.i],o.i);
  else if(t.dataset.act==='copy')copy(citation(o.D,o.i,selIn(card.querySelector('.snip'))));
  else if(t.dataset.act==='full'){const sn=card.querySelector('.snip'),text=o.D.s.t[o.i];
    if(t.dataset.open){sn.innerHTML=snippets(text,ranges(text,allTerms()));t.textContent='Hele tekst';delete t.dataset.open;}
    else{sn.innerHTML=paras(text,ranges(text,allTerms()));t.textContent='Alleen fragment';t.dataset.open=1;}}
});
$('rbody').addEventListener('click',e=>{const t=e.target.closest('[data-act="rcopy"]');if(!t||!RD)return;const sp=t.closest('.sp');copy(citation(RD.D,+sp.dataset.i,selIn(sp)));});
$('rclose').addEventListener('click',closeReader);
$('reader').addEventListener('click',e=>{if(e.target.id==='reader')closeReader();});
$('rprev').addEventListener('click',()=>RD&&openReader(RD.D,RD.it-1,-1));
$('rnext').addEventListener('click',()=>RD&&openReader(RD.D,RD.it+1,-1));
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&RD)closeReader();if(e.key==='/'&&!/INPUT|SELECT|TEXTAREA/.test(document.activeElement.tagName)){e.preventDefault();$('q').focus();}});

/* init */
(function(){
  $('built').textContent=fdate(META.built,true);
  const ys=META.years.map(y=>+y.y);$('span').textContent=Math.min(...ys)+'–'+Math.max(...ys);
  $('spk').innerHTML=SPK.map((x,i)=>i).sort((a,b)=>SPK[a][1]<SPK[b][1]?-1:1).map(i=>'<option value="'+esc(SPK[i][0])+'">').join('');
  $('fp').insertAdjacentHTML('beforeend',PAR.slice().sort((a,b)=>a.localeCompare(b,'nl')).map(p=>'<option>'+esc(p)+'</option>').join(''));
  $('theme').insertAdjacentHTML('beforeend',THEMES.map(g=>'<optgroup label="'+esc(g[0])+'">'+g[1].map(t=>'<option value="'+esc(t[1])+'">'+esc(t[0])+'</option>').join('')+'</optgroup>').join(''));
  fromHash();renderBrowse();loadAll().catch(e=>{$('loadtxt').textContent='Laden mislukt: '+e.message;console.error(e);});
})();
</script>
</body>
</html>
