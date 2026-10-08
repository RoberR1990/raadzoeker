/* Gedeeld door de ontwerpschermen: kop, hulpfuncties, zoeklijst (combobox), uitklapbare rijen, deellinks. */
const $=id=>document.getElementById(id);
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const nf=n=>Number(n).toLocaleString('nl-NL');
const MND=['jan','feb','mrt','apr','mei','jun','jul','aug','sep','okt','nov','dec'];
const MNDL=['januari','februari','maart','april','mei','juni','juli','augustus','september','oktober','november','december'];
const fd=d=>{if(!d)return '';const [y,m,dd]=d.split('-');return +dd+' '+MND[+m-1]+' '+y;};
const fdl=d=>{const [y,m,dd]=d.split('-');return +dd+' '+MNDL[+m-1]+' '+y;};
const slug=s=>s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/&/g,' ').replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
/* citeren en kopiëren (citeer.js): per pagina een functie in RZ_CIT[naam](dataset, knop) die de gegevens levert; knoppen maakt citKnoppen().
   soort: citaat | link | verw | copilot. ds = extra data-attributen (data-id enzovoort). naam = korte beschrijving voor schermlezers. */
window.RZ_CIT=window.RZ_CIT||{};window.rzCiteerKlaar=window.rzCiteerKlaar||Promise.resolve();
function citKnoppen(b,ds,o={}){
  const a=Object.entries(ds||{}).map(([k,v])=>` data-${k}="${esc(v)}"`).join(''),n=o.naam?' '+o.naam:'';
  const bt=(s,t)=>`<button type="button" class="knop wit klein rzc" data-rzc="${s}" data-rzb="${b}"${a} aria-label="${t}${esc(n)}">${t}</button>`;
  return (o.citaat!==false?bt('citaat','Kopieer citaat'):'')+(o.link?bt('link','Kopieer link'):'')+(o.verw?bt('verw','Kopieer verwijzing'):'')+(o.copilot?bt('copilot','Kopieer voor Copilot'):'');
}
const iso=s=>{const m=(s||'').match(/(\d\d)-(\d\d)-(\d{4})/);return m?`${m[3]}-${m[2]}-${m[1]}`:'';};
// loopt het bijwerken achter? Vergelijk met de laatste geplande run (nas/crontab: elke nacht 02:30, werkdagen 9:15-21:15 om de 3 uur),
// met 90 minuten speling voor de run zelf en het online zetten.
function rzAchter(laatste,nu){
  const grens=new Date(nu.getTime()-90*60000);
  for(let i=0;i<4;i++){   // zoek terug naar de laatste geplande starttijd vóór de grens
    const dag=new Date(grens.getFullYear(),grens.getMonth(),grens.getDate()-i),wd=dag.getDay()>=1&&dag.getDay()<=5;
    const tijden=[[2,30]].concat(wd?[[9,15],[12,15],[15,15],[18,15],[21,15]]:[]);
    const voor=tijden.map(([u,m])=>new Date(dag.getFullYear(),dag.getMonth(),dag.getDate(),u,m)).filter(x=>x<=grens);
    if(voor.length)return laatste<voor[voor.length-1];
  }
  return false;
}
window.rzAchter=rzAchter;
const FREQ='Wordt automatisch bijgewerkt: elke nacht, en op werkdagen om 9, 12, 15, 18 en 21 uur.';
const STAND='2026-10-08';   /* stand van de gegevens; ook in src/paden.py */
const dagen=(a,b)=>Math.round((new Date(b)-new Date(a))/864e5);

/* logo: halfrond van negen zetels (de raadzaal), één groen gemarkeerd; woordmerk in kleine letters */
const LOGO=(kleur='#fff',accent='#fff')=>{let s='';const n=9;for(let i=0;i<n;i++){const a=Math.PI*(1-i/(n-1)),x=17+13*Math.cos(a),y=18-13*Math.sin(a);s+=`<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="2.6" fill="${i===6?accent:kleur}" ${i===6?'':'opacity=".75"'}/>`;}
  return `<svg viewBox="0 0 34 20" aria-hidden="true">${s}<circle cx="17" cy="17" r="3.2" fill="${kleur}"/></svg>`;};
/* kop: zoekveld in de kop (vanaf 1100px), vier hoofditems, op telefoon een tabbalk onderin; een oude rz-kop uit de proefperiode wordt opgeruimd */
try{localStorage.removeItem('rz-kop');}catch(e){}
function kop(actief){
  const KLOK='<svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="8" cy="8" r="6.2"/><path d="M8 4.5V8l2.4 1.6"/></svg>';
  const kortStand=fd(STAND).replace(/ \d{4}$/,'');
  const merk=`<a class="merk" href="./" aria-label="raadzoeker, naar de startpagina"><img src="logo-wit.svg" alt="" width="53" height="40"><span class="merktekst"><b>raadzoeker</b><small>onofficieel</small></span></a>`;
  {
    const hb=[['domeinen','Dossiers','domeinen.html'],['gebieden','Gebieden','wijk.html'],['vergaderingen','Vergaderingen','vergaderingen.html'],['beloofd','Beloofd','beloofd.html'],['lab','Inzichten','lab.html']];
    const act=actief==='verkenner'?'lab':actief,ab=x=>`<a href="${x[2]}" class="${x[0]===act?'on':''}"${x[0]===act?' aria-current="page"':''}>${x[1]}</a>`;
    const LENS='<svg viewBox="0 0 20 20" width="20" height="20" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2"><circle cx="8.5" cy="8.5" r="5.5"/><path d="M13 13l5 5"/></svg>';
    document.documentElement.classList.add('kop-b');
    const h=document.querySelector('header.balk');h.classList.add('kb');if(actief==='zoeken'||document.querySelector('.zoekrij #zoek'))h.classList.add('zonderzoek');
    h.innerHTML=`<div class="in">${merk}
    <form class="zoekveld kopzoek" id="kopzoekvorm" role="search" autocomplete="off"><span class="lens">${LENS}</span><input id="kopzoek" type="search" role="combobox" aria-expanded="false" aria-controls="kopkeuze" aria-autocomplete="list" aria-label="Zoek in raad, stukken, dossiers" placeholder="Zoek in raad, stukken, dossiers…" enterkeyhint="search"><kbd class="slash" aria-hidden="true">/</kbd><ul class="keuze" id="kopkeuze" role="listbox" aria-label="Suggesties"></ul></form>
    <div class="menupaneel" id="menupaneel"><nav aria-label="Hoofdmenu">${hb.map(ab).join('')}</nav></div>
    <div class="kopknoppen"><a class="kopklok" id="bijgewerkt" href="nieuw.html" title="${esc(FREQ)}" aria-label="Wat is er nieuw — bijgewerkt ${fd(STAND)}">${KLOK}<span class="sr t">${kortStand}</span></a></div></div>`;
  }
  kopZoekB(actief);tabbalkB(actief);
  // laatste automatische update (status.json schrijft de NAS na elke geslaagde run)
  fetch('data/status.json',{cache:'no-store'}).then(r=>r.ok?r.json():null).then(st=>{if(!st||!st.laatste)return;const el=document.getElementById('bijgewerkt');if(!el)return;
    const d=new Date(st.laatste),t=d.getDate()+' '+MND[d.getMonth()]+' '+String(d.getHours()).padStart(2,'0')+':'+String(d.getMinutes()).padStart(2,'0');
    document.querySelectorAll('#bijgewerkt .t,.voetbij .t,.meersheet .t').forEach(x=>x.textContent=t);el.setAttribute('aria-label','Wat is er nieuw — bijgewerkt '+t);
    if(rzAchter(d,new Date())){const m='Bijwerken loopt achter: de laatste geslaagde update was '+t+'.';   // een geplande run is niet gelukt
      document.querySelectorAll('#bijgewerkt,.voetbij,.meersheet .bijgewerkt').forEach(x=>{x.classList.add('achter');x.title=m;});
      document.querySelectorAll('.voetbij .t,.meersheet .t').forEach(x=>x.textContent=t+' · loopt achter');el.setAttribute('aria-label',m);}}).catch(()=>{});
  voetB();
  // rondleiding, hulpknop en welkomstvenster (tour.js)
  if(!document.getElementById('rz-tour')){const t=document.createElement('script');t.id='rz-tour';t.src='tour.js?v=15';document.body.appendChild(t);const w=document.createElement('script');w.src='woorden.js?v=3';document.body.appendChild(w);const r=document.createElement('script');r.src='stad.js?v=4';document.body.appendChild(r);
    const c=document.createElement('script');c.src='citeer.js?v=1';window.rzCiteerKlaar=new Promise(ok=>{c.onload=ok;c.onerror=ok;});document.body.appendChild(c);}
  const ic=document.createElement('link');ic.rel='icon';ic.type='image/svg+xml';ic.href='logo.svg';document.head.appendChild(ic);
}
/* zoekveld in de kop (vanaf 1100px) en dezelfde koppeling voor de zoeklaag op mobiel; Enter zoekt altijd, een gekozen suggestie opent dossier of gebied */
let ZOEKALLE=null;
function zoekKoppel(inv,keuze,vorm){
  let gekozen=false;
  const alle=()=>ZOEKALLE||[];
  const haal=()=>{if(ZOEKALLE)return;ZOEKALLE=[];fetch('d/index.json').then(r=>r.json()).then(IX=>{ZOEKALLE=IX.d.filter(x=>x.soort!=='kruising').map(x=>Object.assign({sub:[],termen:''},x));}).catch(()=>{ZOEKALLE=null;});};
  inv.addEventListener('focus',haal);
  inv.addEventListener('input',()=>{gekozen=false;keuze.classList.add('geen');});
  inv.addEventListener('keydown',e=>{if(e.key==='ArrowDown'||e.key==='ArrowUp'){if(!gekozen&&keuze.classList.contains('on')){e.preventDefault();e.stopImmediatePropagation();}gekozen=true;keuze.classList.remove('geen');}
    else if(e.key==='Enter'&&!gekozen){e.preventDefault();e.stopImmediatePropagation();const q=inv.value.trim();if(q)location.href='zoek.html?q='+encodeURIComponent(q);}});
  zoeklijst(inv,keuze,alle,x=>{location.href=(x.soort==='gebied'?'wijk.html#':'dossier.html#')+x.slug;});
  vorm.addEventListener('submit',e=>{e.preventDefault();const q=inv.value.trim();if(q)location.href='zoek.html?q='+encodeURIComponent(q);});
}
function kopZoekB(actief){
  zoekKoppel($('kopzoek'),$('kopkeuze'),$('kopzoekvorm'));
  // '/' zet de cursor in het kopveld (op zoek.html zorgt de pagina zelf); op een telefoon opent de zoeklaag
  addEventListener('keydown',e=>{if(e.key!=='/'||e.ctrlKey||e.metaKey||e.altKey||actief==='zoeken'||/input|textarea|select/i.test(document.activeElement.tagName)||document.activeElement.isContentEditable)return;
    e.preventDefault();e.stopImmediatePropagation();const t=$('tabzoek');if(t&&getComputedStyle(t.closest('.tabbalk')).display!=='none')t.click();else $('kopzoek').focus();},true);
}
/* onder 1100px: vaste tabbalk (Zoek, Dossiers, Gebieden, Vergaderingen, Meer), zoeklaag en Meer-sheet */
function tabbalkB(actief){
  const ik=d=>`<svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${d}</svg>`;
  const IK={zoek:ik('<circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5L21 21"/>'),dossiers:ik('<path d="M3 7a2 2 0 0 1 2-2h4l2 2.5h8a2 2 0 0 1 2 2V18a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>'),gebieden:ik('<path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>'),verg:ik('<rect x="3.5" y="5" width="17" height="15.5" rx="2"/><path d="M3.5 10h17M8 3v4M16 3v4"/>'),meer:ik('<circle cx="5.5" cy="12" r="1.2"/><circle cx="12" cy="12" r="1.2"/><circle cx="18.5" cy="12" r="1.2"/>'),x:ik('<path d="M6 6l12 12M18 6L6 18"/>')};
  const MEER=['beloofd','lab','verkenner','over','hulp','volg','nieuw','akkoord'],opMeer=MEER.includes(actief)||(!actief&&MEER.includes(location.pathname.split('/').pop().replace(/\.html$/,'')));
  const act=actief==='dossier'?'domeinen':actief;
  const tab=(k,t,h,id)=>{const on=h&&act===k;return h?`<a href="${h}" class="tab${on?' on':''}"${on?' aria-current="page"':''}>${IK[id]}<span>${t}</span></a>`:'';};
  const nav=document.createElement('nav');nav.className='tabbalk';nav.setAttribute('aria-label','Hoofdnavigatie');
  nav.innerHTML=`<button type="button" class="tab" id="tabzoek" aria-haspopup="dialog" aria-expanded="false"${actief==='zoeken'?' aria-current="page"':''}>${IK.zoek}<span>Zoek</span></button>${tab('domeinen','Dossiers','domeinen.html','dossiers')}${tab('gebieden','Gebieden','wijk.html','gebieden')}${tab('vergaderingen','Vergaderingen','vergaderingen.html','verg')}<button type="button" class="tab${opMeer?' on':''}" id="tabmeer" aria-haspopup="dialog" aria-expanded="false"${opMeer?' aria-current="page"':''}>${IK.meer}<span>Meer</span></button>`;
  if(actief==='zoeken')nav.querySelector('#tabzoek').classList.add('on');
  const laag=document.createElement('div');laag.className='zoeklaag';laag.id='zoeklaag';laag.hidden=true;laag.setAttribute('role','dialog');laag.setAttribute('aria-modal','true');laag.setAttribute('aria-label','Zoeken');
  laag.innerHTML=`<div class="zl-in"><form class="zoekveld zl-vorm" id="zlvorm" role="search" autocomplete="off"><span class="lens">${IK.zoek}</span><input id="zlzoek" type="search" role="combobox" aria-expanded="false" aria-controls="zlkeuze" aria-autocomplete="list" aria-label="Zoek in raad, stukken, dossiers" placeholder="Zoek in raad, stukken, dossiers…" enterkeyhint="search"></form><button type="button" class="zl-sluit" id="zlsluit" aria-label="Sluit zoeken">${IK.x}</button></div><ul class="keuze" id="zlkeuze" role="listbox" aria-label="Suggesties"></ul><p class="zl-hint">Typ een woord, een dossier of een gebied en druk op Enter om te zoeken in alles wat de raad zegt en schrijft.</p>`;
  const sheet=document.createElement('div');sheet.className='meersheet';sheet.id='meersheet';sheet.hidden=true;
  const ml=(h,t,extra='')=>`<a href="${h}"${extra}>${t}</a>`;
  sheet.innerHTML=`<div class="ms-doek" data-sluit></div><div class="ms-vel" role="dialog" aria-modal="true" aria-label="Meer"><div class="ms-kop"><b>Meer</b><button type="button" class="zl-sluit" id="mssluit" aria-label="Sluit menu">${IK.x}</button></div><nav aria-label="Meer">${ml('beloofd.html','Beloofd')}${ml('lab.html','Inzichten')}${ml('verkenner.html','Verkenner')}${ml('volg.html','Volgen')}${ml('over.html','Over')}${ml('hulp.html','Hulp')}<a class="bijgewerkt" href="nieuw.html">Wat is nieuw <small>bijgewerkt <span class="t">${fd(STAND).replace(/ \d{4}$/,'')}</span></small></a></nav></div>`;
  [...sheet.querySelectorAll('nav a')].forEach(a=>{if((a.getAttribute('href')||'').startsWith(actief+'.html'))a.setAttribute('aria-current','page');});
  document.body.append(nav,laag,sheet);
  zoekKoppel($('zlzoek'),$('zlkeuze'),$('zlvorm'));
  let open=null,terug=null;
  const foc=el=>[...el.querySelectorAll('a[href],button,input')].filter(x=>!x.disabled&&x.offsetParent!==null);
  const zet=(naam,o)=>{const el=naam==='zoek'?laag:sheet,kn=naam==='zoek'?$('tabzoek'):$('tabmeer');
    if(o){if(open&&open!==naam)zet(open,false);terug=kn;el.hidden=false;kn.setAttribute('aria-expanded','true');document.documentElement.classList.add('zl-open');open=naam;
      setTimeout(()=>{(naam==='zoek'?$('zlzoek'):el.querySelector('nav a')).focus();},30);}
    else if(open===naam){el.hidden=true;kn.setAttribute('aria-expanded','false');document.documentElement.classList.remove('zl-open');open=null;if(terug)terug.focus();
      if(naam==='zoek'){$('zlzoek').value='';$('zlkeuze').classList.remove('on');}}};
  $('tabzoek').onclick=()=>{const p=document.querySelector('#q,#zk,#zoek,#zf input');if(actief==='zoeken'&&p){p.scrollIntoView({block:'center'});p.focus();return;}zet('zoek',open!=='zoek');};
  $('tabmeer').onclick=()=>zet('meer',open!=='meer');
  $('zlsluit').onclick=()=>zet('zoek',false);$('mssluit').onclick=()=>zet('meer',false);
  sheet.querySelector('[data-sluit]').onclick=()=>zet('meer',false);
  laag.addEventListener('click',e=>{if(e.target===laag)zet('zoek',false);});
  addEventListener('keydown',e=>{if(!open)return;const el=open==='zoek'?laag:sheet;
    if(e.key==='Escape'){if(open==='zoek'&&$('zlkeuze').classList.contains('on')){$('zlkeuze').classList.remove('on');return;}e.preventDefault();zet(open,false);}
    else if(e.key==='Tab'){const f=foc(el);if(!f.length)return;const i=f.indexOf(document.activeElement);if(e.shiftKey&&i<=0){e.preventDefault();f[f.length-1].focus();}else if(!e.shiftKey&&(i===f.length-1||i<0)){e.preventDefault();f[0].focus();}}});
  matchMedia('(min-width:1100px)').addEventListener('change',e=>{if(e.matches&&open)zet(open,false);});
}
/* voettekst met Over, Hulp, Privacy, Verkenner en de stand van de gegevens (alleen als de pagina er nog geen heeft) */
function voetB(){
  if(document.querySelector('footer.rz-voet')||document.querySelector('body>footer'))return;
  const f=document.createElement('footer');f.className='rz-voet';
  f.innerHTML=`<div class="in"><nav aria-label="Over deze site"><a href="over.html">Over</a><a href="hulp.html">Hulp</a><a href="over.html#privacy">Privacy</a><a href="verkenner.html">Verkenner</a><a class="voetbij" href="nieuw.html" title="${esc(FREQ)}" aria-label="Wat is er nieuw — bijgewerkt ${fd(STAND).replace(/ \d{4}$/,'')}">bijgewerkt <span class="t">${fd(STAND).replace(/ \d{4}$/,'')}</span></a></nav></div>`;
  document.body.appendChild(f);
}
/* zoeken in onderwerpen of gebieden; kiezen roept kies(d) aan */
/* bewerkingsafstand (Levenshtein), voor 'bedoel je…' bij tikfouten */
function afstand(a,b){if(Math.abs(a.length-b.length)>3)return 9;let v=[...Array(b.length+1).keys()];for(let i=1;i<=a.length;i++){let p=v[0];v[0]=i;for(let j=1;j<=b.length;j++){const t=v[j];v[j]=Math.min(v[j]+1,v[j-1]+1,p+(a[i-1]===b[j-1]?0:1));p=t;}}return v[b.length];}
/* beste 'bedoel je…' uit een lijst namen: per woord vergelijken, tolerantie naar woordlengte */
function bedoelJe(q,namen,n=3){q=q.toLowerCase().trim();if(q.length<3)return[];
  return namen.map(x=>{const w=x.toLowerCase().split(/[^a-z0-9à-ÿ]+/).filter(Boolean);const d=Math.min(...w.map(y=>afstand(q,y.slice(0,Math.max(q.length,y.length)))),afstand(q,x.toLowerCase()));return [d,x];})
    .filter(([d])=>d<=(q.length<6?1:2)).sort((a,b)=>a[0]-b[0]).slice(0,n).map(x=>x[1]);}
function zoeklijst(input,lijst,bron,kies){
  let hits=[],act=0;
  const toon=()=>{lijst.innerHTML=hits.length?hits.map((d,i)=>`<li role="option" id="opt${i}" aria-selected="${i===act}" data-i="${i}">${esc(d.naam)} <span class="sub">· ${esc(d.groep)}</span></li>`).join(''):leegLijst();
    lijst.classList.add('on');input.setAttribute('aria-expanded','true');input.setAttribute('aria-activedescendant',hits.length?'opt'+act:'');};
  const leegLijst=()=>{const q=input.value.trim(),b=bedoelJe(q,bron().map(d=>d.naam));
    return `<li class="leeg" role="option" aria-disabled="true">Geen dossier met die naam.${b.length?` Bedoel je ${b.map(x=>`<a href="#" data-bedoel="${esc(x)}">${esc(x)}</a>`).join(' of ')}?`:''} <a href="zoek.html?q=${encodeURIComponent(q)}">Zoek '${esc(q)}' in alles wat er gezegd en geschreven is →</a></li>`;};
  lijst.addEventListener('mousedown',e=>{const a=e.target.closest('[data-bedoel]');if(!a)return;e.preventDefault();input.value=a.dataset.bedoel;input.dispatchEvent(new Event('input'));});
  const sluit=()=>{lijst.classList.remove('on');input.setAttribute('aria-expanded','false');};
  input.addEventListener('input',()=>{const q=input.value.trim().toLowerCase();if(!q){sluit();return;}
    hits=bron().map(d=>{const n=d.naam.toLowerCase();return [n.startsWith(q)?3:n.includes(q)?2:d.sub.some(x=>x.toLowerCase().includes(q))?1.5:d.termen.toLowerCase().includes(q)?1:0,d];}).filter(x=>x[0]).sort((a,b)=>b[0]-a[0]).slice(0,10).map(x=>x[1]);act=0;toon();});
  input.addEventListener('keydown',e=>{if(!lijst.classList.contains('on'))return;
    if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();if(hits.length){act=(act+(e.key==='ArrowDown'?1:-1)+hits.length)%hits.length;toon();}}
    else if(e.key==='Enter'&&hits[act]){e.preventDefault();sluit();input.value='';kies(hits[act]);}
    else if(e.key==='Escape')sluit();});
  lijst.addEventListener('click',e=>{const li=e.target.closest('[data-i]');if(li){sluit();input.value='';kies(hits[+li.dataset.i]);}});
  document.addEventListener('click',e=>{if(!e.target.closest('.zoekveld'))sluit();});
}
/* onderwerp/gebied zoeken op #slug of #nummer */
function uitHash(lijst){const h=decodeURIComponent(location.hash.slice(1));if(!h)return null;return lijst.find(d=>slug(d.naam)===h)||(/^\d+$/.test(h)?lijst.find(d=>d.id===+h):null);}

/* uitklapbare rij voor een motie, toezegging of ander stuk
   r=[datum,titel,indiener,statustekst,url,bb,context] ; soort='motie'|'toez'|'stuk' ; stand=peildatum */
function rij(r,soort,stand){
  const dl=iso((r[3].match(/verwacht ([\d-]+)/)||[])[1]),af=iso((r[3].match(/afgedaan ([\d-]+)/)||[])[1]);
  const laat=dl&&!af&&dl<stand,isAf=/afgedaan(?! )|afgedaan \d/.test(r[3])&&!/nog niet afgedaan/.test(r[3]);
  const status=isAf?`<span><span class="stip af"></span>Afgedaan${af?' op '+fd(af):''}</span>`:laat?`<span><span class="stip laat"></span>${dagen(dl,stand)} dagen over de termijn</span>`:dl?`<span><span class="stip open"></span>Afdoening verwacht ${fd(dl)}</span>`:r[3]?`<span>${esc(r[3])}</span>`:'';
  const c=r[6]||{};let ctx='';
  if(c.s)ctx+=stemHTML(c.s);
  if(c.c)ctx+=`<div><b>Aanleiding</b> ‘${esc(c.c)}’</div>`;
  if(c.v)ctx+=`<div><b>Verzoek aan het college</b> ‘${esc(c.v)}’</div>`;
  if(c.o)ctx+=`<div><b>Toegezegd</b> ‘${esc(c.o)}’</div>`;
  ctx+=`<div><a href="${esc(r[4])}" target="_blank" rel="noopener">Open in iBabs${r[5]?' ('+esc(r[5])+')':''}</a></div>`;
  return `<details class="item"><summary><span class="meta"><span class="d">${fd(r[0])}</span>${status}${r[2]?`<span class="wie">${esc(r[2])}</span>`:''}</span><span class="t">${esc(r[1])}</span><span class="pijl" aria-hidden="true">›</span></summary><div class="ctx">${ctx}</div></details>`;
}
/* debat met letterlijk fragment: x=[datum,agendaId,titel,treffers,fragment,start,lengte,sprekers,soort] */
function debatRij(x,termen){
  const f=x[4]||'',a=x[5],l=x[6];const fr=a>=0?esc(f.slice(0,a))+'<mark>'+esc(f.slice(a,a+l))+'</mark>'+esc(f.slice(a+l)):esc(f);
  const archief=`zoek.html#q=${encodeURIComponent(termen)}&van=${x[0].slice(0,4)}&tot=${x[0].slice(0,4)}`;
  return `<details class="item"><summary><span class="meta"><span class="d">${fd(x[0])}</span><span>${nf(x[3])} ${x[5]<0?'spreekbeurten':'keer genoemd'}</span>${x[7]&&x[7].length?`<span class="wie">${esc(x[7].join(', '))}</span>`:''}</span><span class="t">${esc(x[2]||'Raadsvergadering')}</span><span class="pijl" aria-hidden="true">›</span></summary>
    <div class="ctx"><div>‘${fr}’${x[8]===4?' <span class="sub">(automatische ondertiteling)</span>':''}</div>
    <div><a href="${archief}">Lees het debat</a> · <a href="https://gemeenteraad.rotterdam.nl/Agenda/Index/${esc(x[1])}" target="_blank" rel="noopener">Vergadering en video in iBabs</a></div></div></details>`;
}
/* deellinks: e-mail, Teams, WhatsApp en kopiëren */
let DEELIX=null;   /* deel/index.json: slugs met een deelpagina (og-voorvertoning), geschreven door src/deelkaart.py */
function deel(el,titel,url,slug){
  const maak=url=>{const u=encodeURIComponent(url),t=encodeURIComponent(titel);
    el.innerHTML=`<span class="sub">Delen:</span> <a href="mailto:?subject=${t}&body=${t}%0A${u}">E-mail</a> · <a href="https://teams.microsoft.com/share?href=${u}&msgText=${t}" target="_blank" rel="noopener">Teams</a> · <a href="https://wa.me/?text=${t}%20${u}" target="_blank" rel="noopener">WhatsApp</a> · <button type="button" class="kopie" style="font:inherit;background:none;border:0;padding:0;text-decoration:underline;cursor:pointer">Kopieer link</button>`;
    el.querySelector('.kopie').addEventListener('click',e=>{const k=e.target;if(window.rzKopieer){rzKopieer(url,'Link gekopieerd').then(ok=>{if(ok)k.textContent='Link gekopieerd';});return;}navigator.clipboard.writeText(url).then(()=>{k.textContent='Link gekopieerd';},()=>{prompt('Kopieer deze link',url);});});};
  maak(url);
  if(slug){DEELIX=DEELIX||fetch('deel/index.json').then(r=>r.ok?r.json():[]).catch(()=>[]);
    DEELIX.then(l=>{if(l.includes(slug)&&el.isConnected){maak('https://raadzoeker.nl/deel/'+slug+'.html');}});}
}

/* stemhalfrond: 45 zetels, voor groen, tegen grijs; s=[aangenomen,voor,tegen,zijde,fracties] uit de notulen */
const ZETELS=(()=>{const rij=[[1,15],[.84,12],[.68,10],[.52,8]],z=[];for(const [r,n] of rij)for(let i=0;i<n;i++){const a=Math.PI*(1-i/(n-1));z.push([a,60+52*r*Math.cos(a),58-52*r*Math.sin(a)]);}return z.sort((p,q)=>q[0]-p[0]);})();
function stemHTML(s){
  const [aan,voor,tegen,zijde,fr]=s;
  if(voor<0)return `<div><b>Stemming</b> ${aan?'Aangenomen':'Verworpen'} zonder hoofdelijke telling (meestal: met algemene stemmen of zonder stemming).</div>`;
  const tot=voor+tegen;let dots='';ZETELS.forEach((z,i)=>{const kl=i<voor?'#00811F':i<tot?'#65757C':'#DBE7EA';dots+=`<circle cx="${z[1].toFixed(1)}" cy="${z[2].toFixed(1)}" r="2.9" fill="${kl}"/>`;});
  return `<div style="display:flex;gap:16px;align-items:center;flex-wrap:wrap"><svg viewBox="0 0 120 62" width="132" height="68" role="img" aria-label="${voor} voor, ${tegen} tegen">${dots}</svg>
    <div><b>${aan?'Aangenomen':'Verworpen'}</b> met <span class="num">${voor}</span> stemmen voor en <span class="num">${tegen}</span> tegen.${fr?`<br><span class="sub">${zijde==='v'?'Voor':'Tegen'} stemden: ${esc(fr)}.</span>`:''}</div></div>`;
}

/* fout melden: venster met tekstvak, stuurt de pagina en waar het over gaat naar /api/fout (anoniem) */
function rzFout(over){
  document.getElementById('rz-fout')?.remove();
  const d=document.createElement('div');d.id='rz-fout';d.setAttribute('role','dialog');d.setAttribute('aria-modal','true');d.setAttribute('aria-labelledby','rzf-t');
  d.innerHTML=`<div class="rzf-laag"></div><form class="rzf"><h2 id="rzf-t">Fout melden</h2>
    <p>Klopt er iets niet, bijvoorbeeld een samenvatting, citaat, naam of koppeling? Laat het weten; dan kijk ik ernaar.</p>
    ${over?`<p class="rzf-over">Over: ${esc(over).slice(0,300)}</p>`:''}
    <label for="rzf-x">Wat klopt er niet?</label><textarea id="rzf-x" rows="4" maxlength="2000" required></textarea>
    <p class="rzf-klein">Je melding is anoniem: we bewaren alleen de pagina en je tekst. Wil je antwoord, zet dan zelf een e-mailadres in je bericht.</p>
    <div class="rzf-rij"><button type="submit">Versturen</button><button type="button" class="wit" data-a="weg">Annuleren</button><span class="rzf-st" aria-live="polite"></span></div></form>`;
  document.body.appendChild(d);const x=d.querySelector('textarea');x.focus();
  const weg=()=>d.remove();d.querySelector('.rzf-laag').onclick=weg;d.querySelector('[data-a=weg]').onclick=weg;
  d.addEventListener('keydown',e=>{if(e.key==='Escape')weg();});
  d.querySelector('form').onsubmit=async e=>{e.preventDefault();const st=d.querySelector('.rzf-st');st.textContent='Versturen…';
    try{const r=await fetch('/api/fout',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({pagina:location.href,over:over||'',tekst:x.value})});
      if(!r.ok)throw 0;d.querySelector('form').innerHTML='<h2>Dank je!</h2><p>Je melding is ontvangen.</p><div class="rzf-rij"><button type="button">Sluiten</button></div>';d.querySelector('form button').onclick=weg;}
    catch(_){st.textContent='Versturen lukte niet. Probeer het later nog eens.';}};
}
(()=>{const s=document.createElement('style');s.textContent=`#rz-fout{position:fixed;inset:0;z-index:1000;display:flex;align-items:center;justify-content:center;padding:16px}
.rzf-laag{position:absolute;inset:0;background:rgba(0,25,12,.55)}.rzf{position:relative;background:var(--wit);color:var(--zwart);border-radius:10px;padding:22px 24px;max-width:480px;width:100%;box-shadow:0 10px 40px rgba(0,0,0,.3)}
.rzf h2{margin:0 0 8px;font-size:21px}.rzf p{margin:0 0 10px;font-size:15px;line-height:1.5}.rzf label{font-weight:700;font-size:14px}.rzf textarea{width:100%;box-sizing:border-box;font:15px var(--font);padding:8px;border:1.5px solid var(--lijn);border-radius:6px;margin:4px 0 8px;background:var(--wit);color:var(--zwart)}
.rzf-over{background:var(--grijs);border-radius:6px;padding:6px 10px;font-size:13px!important}.rzf-klein{font-size:12px!important;color:var(--sub)}
.rzf-rij{display:flex;gap:8px;align-items:center;flex-wrap:wrap}.rzf button{font:700 15px var(--font);border-radius:999px;padding:8px 18px;border:2px solid var(--groen);background:var(--groen);color:#fff;cursor:pointer}.rzf button.wit{background:var(--wit);color:var(--groen)}.rzf-st{font-size:13px;color:var(--sub)}`;document.head.appendChild(s);})();

/* ---------- volgen: onderwerpen, domeinen en gebieden volgen (in je eigen browser), met optioneel pushmeldingen ---------- */
const RZV={
  pub:'BCQ5wiH7FYmjbMIOViN3DznTaCF-4ClUMhS7n1KqXt4fFbNWBp947WtCU_nhCw-SugxSNpFqvyI-t3C-9DVSBiY',
  lijst(){try{return JSON.parse(localStorage.getItem('rz-volg')||'{}');}catch(e){return {};}},
  bewaar(L){try{localStorage.setItem('rz-volg',JSON.stringify(L));}catch(e){}},
  volgt(s){return !!this.lijst()[s];},
  zet(s,naam){const L=this.lijst();L[s]={naam,gezien:new Date(Date.now()-14*864e5).toISOString().slice(0,10)};   // de laatste twee weken tellen als nieuw
    this.bewaar(L);this.sync();},
  weg(s){const L=this.lijst();delete L[s];this.bewaar(L);this.sync();},
  gezien(s){const L=this.lijst();if(L[s]){L[s].gezien=new Date().toISOString().slice(0,10);this.bewaar(L);}},
  data:null,
  async nieuws(){if(!Object.keys(this.lijst()).length)return {};this.data=this.data||fetch('volg.json',{cache:'no-cache'}).then(r=>r.ok?r.json():{d:{}}).catch(()=>({d:{}}));
    const D=(await this.data).d||{},L=this.lijst(),uit={};for(const s in L)uit[s]=((D[s]||{}).i||[]).filter(i=>i[0]>L[s].gezien);return uit;},
  pushKan(){return 'serviceWorker' in navigator&&'PushManager' in window&&'Notification' in window;},
  async sub(){if(!this.pushKan())return null;const r=await navigator.serviceWorker.getRegistration('/');return r?r.pushManager.getSubscription():null;},
  async pushAan(){
    if(!this.pushKan())throw new Error('kan niet');
    const reg=await navigator.serviceWorker.register('/sw.js',{scope:'/'});await navigator.serviceWorker.ready;
    if(await Notification.requestPermission()!=='granted')throw new Error('geweigerd');
    const k=Uint8Array.from(atob(this.pub.replace(/-/g,'+').replace(/_/g,'/')),c=>c.charCodeAt(0));
    const s=(await reg.pushManager.getSubscription())||await reg.pushManager.subscribe({userVisibleOnly:true,applicationServerKey:k});
    await this.sync(s);return true;},
  async pushUit(){const s=await this.sub();if(!s)return;await fetch('/api/volg',{method:'DELETE',headers:{'content-type':'application/json'},body:JSON.stringify({endpoint:s.endpoint})}).catch(()=>{});await s.unsubscribe();},
  async sync(s){s=s||await this.sub().catch(()=>null);if(!s)return;
    await fetch('/api/volg',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({endpoint:s.endpoint,onderwerpen:Object.keys(this.lijst())})}).catch(()=>{});}
};
window.RZV=RZV;
// knop 'Volg' (in de kop van een dossier- of gebiedspagina)
function volgKnop(slug,naam){return `<button type="button" class="knop wit volgknop" data-volg="${esc(slug)}" data-naam="${esc(naam)}" aria-pressed="${RZV.volgt(slug)}">${RZV.volgt(slug)?'★ Volgend':'☆ Volg'}</button>`;}
document.addEventListener('click',e=>{const b=e.target.closest('[data-volg]');if(!b)return;const s=b.dataset.volg;
  if(RZV.volgt(s)){RZV.weg(s);}else{RZV.zet(s,b.dataset.naam);window.rzToast&&rzToast('Je volgt nu '+b.dataset.naam+'. Nieuws zie je bij ★ bovenaan.');}
  document.querySelectorAll(`[data-volg="${CSS.escape(s)}"]`).forEach(x=>{x.setAttribute('aria-pressed',RZV.volgt(s));x.textContent=RZV.volgt(s)?'★ Volgend':'☆ Volg';});volgBel();});
// ster met aantal nieuwe items in de kop, alleen als je iets volgt
async function volgBel(){const nav=document.querySelector('header .kopknoppen');if(!nav)return;let a=nav.querySelector('.volgbel');
  if(!Object.keys(RZV.lijst()).length){a&&a.remove();return;}
  if(!a){a=document.createElement('a');a.className='volgbel';a.href='volg.html';a.title='Wat je volgt';a.innerHTML='★<span class="n"></span>';nav.insertBefore(a,nav.firstChild);}
  const N=await RZV.nieuws(),n=Object.values(N).reduce((x,l)=>x+l.length,0);a.querySelector('.n').textContent=n?n:'';a.setAttribute('aria-label',n?`Wat je volgt: ${n} nieuw`:'Wat je volgt');}
(()=>{const s=document.createElement('style');s.textContent=`.volgbel{position:relative;font-size:20px;text-decoration:none;color:#fff;padding:6px 10px;min-height:44px;display:inline-flex;align-items:center}.volgbel .n:not(:empty){position:absolute;top:0;right:0;background:#E56E02;color:#fff;border-radius:999px;font-size:11px;font-weight:700;padding:1px 5px;line-height:1.3}
.volgknop[aria-pressed=true]{background:var(--groen-zacht);border-color:var(--groen);color:var(--zwart)}`;document.head.appendChild(s);
  const m=document.createElement('link');m.rel='manifest';m.href='/manifest.webmanifest';document.head.appendChild(m);
  setTimeout(volgBel,300);})();
