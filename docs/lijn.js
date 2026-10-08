/* Dossiertijdlijn (7-10-2026): één onderwerp, domein of gebied als lijn door de tijd. Links de raad (debatten, moties, vragen,
   rapporten, wijkraden), rechts het college (toezeggingen, brieven, voorstellen, besluiten, afdoeningen). Geen AI.
   Data: lijn/<slug>.json en lijn/index.json (src/tracker.py).
   Publiek:
     rzLijnIndex()            belofte van {slug: aantal}; zonder bestand {}
     rzLijnAantal(slug)       aantal gebeurtenissen (0 = geen tijdlijn), pas na rzLijnIndex()
     rzLijnLaad(slug)         belofte van de gegevens (gecachet)
     rzLijn(el, slug, opties) tekent in el. Opties: open (bool, standaard dicht = voorproefje), toggle (knop 'Toon de hele tijdlijn',
                              standaard aan), intro (uitleg boven de strook, standaard aan), wrap (element dat getoond wordt zodra er een
                              tijdlijn is; blijft verborgen zonder), scroll (scrol na het tekenen naar wrap), onToggle(open) (voor de link)
     rzLijnZet(el, open, scrol)  open of dicht zetten, zonder onToggle (voor hashchange)
     rzLijnVideo(ref, sec, titel) opent het videovenster van keten.js (laadt keten.js/keten.css alleen als het nodig is)
   De toestand van filters en open jaren blijft per dossier bewaard in het geheugen zolang de pagina openstaat. */
(function(){
'use strict';
const BASIS=(document.currentScript&&document.currentScript.src)||location.href;
const TYPE={
  debat:{g:'debat',l:'debat',s:'debat'},motie:{g:'motie',l:'motie',s:'motie'},amendement:{g:'motie',l:'amendement',s:'motie'},
  toez:{g:'toez',l:'toezegging',s:'toez'},afdoening:{g:'afd',l:'afdoening',s:'afd'},brief:{g:'brief',l:'brief',s:'brief'},
  vragen:{g:'vragen',l:'vragen',s:'vragen'},voorstel:{g:'voorstel',l:'voorstel',s:'voorstel'},besluit:{g:'voorstel',l:'besluit',s:'besluit'},
  rapport:{g:'rapport',l:'rapport',s:'rapport'},wijk:{g:'wijk',l:'wijkraad',s:'wijk'}};
const GROEPEN=[['debat','Debatten','debat'],['motie','Moties','motie'],['toez','Toezeggingen','toez'],['afd','Afdoeningen','afd'],['brief','Brieven','brief'],
  ['vragen','Vragen','vragen'],['voorstel','Voorstellen en besluiten','voorstel'],['rapport','Rapporten','rapport'],['wijk','Wijkraden','wijk']];
const GROOT=150,LIM=60,ITEM='https://gemeenteraad.rotterdam.nl/Reports/Item/';
const reduced=()=>matchMedia('(prefers-reduced-motion: reduce)').matches;

/* ---------- gegevens ---------- */
let IDX=null;const LAAD={},CACHE={},STAAT={};
function rzLijnIndex(){return IDX||(IDX=fetch(new URL('lijn/index.json',BASIS)).then(r=>r.ok?r.json():{}).catch(()=>({})).then(x=>(window.__lijnIx=x)));}
function rzLijnAantal(s){return (window.__lijnIx&&window.__lijnIx[s])||0;}
function rzLijnLaad(slug){
  if(CACHE[slug])return Promise.resolve(CACHE[slug]);
  return LAAD[slug]||(LAAD[slug]=fetch(new URL('lijn/'+slug+'.json',BASIS)).then(r=>{if(!r.ok)throw 0;return r.json();}).then(j=>(CACHE[slug]=bouw(slug,j))));
}
function bouw(slug,j){
  const E=j.e.map((a,i)=>{const t=TYPE[a[1]]||TYPE.brief;return {i,d:a[0],t:a[1],k:a[2]==='c'?'c':'r',ti:a[3],su:a[4]||'',u:a[5],x:a[6]||{},j:+a[0].slice(0,4),q:Math.floor((+a[0].slice(5,7)-1)/3),g:t.g,h:-1};});
  const byU=new Map(),byT=new Map(),byId=new Map(),n={},kids=new Map();let nOpen=0;
  E.forEach(e=>{n[e.g]=(n[e.g]||0)+1;byId.set(e.u.split('/').pop(),e.i);
    if(e.g==='motie'||e.g==='toez'){e.h=e.i;if(!byU.has(e.u))byU.set(e.u,[]);byU.get(e.u).push(e.i);if(!byT.has(e.ti))byT.set(e.ti,[]);byT.get(e.ti).push(e.i);if(e.x.st===4)nOpen++;}});
  E.forEach(e=>{
    if(e.g==='afd'){const l=byU.get(e.u);if(l)e.h=l[0];}
    else if(e.g==='brief'&&e.x.bij){const l=byT.get(e.x.bij);if(l){const m=l.find(i=>E[i].d<=e.d);e.h=m!==undefined?m:l[l.length-1];}}});
  E.forEach(e=>{if(e.h===e.i&&e.x.stap)e.x.stap.forEach(s=>{if(s[3]){const b=byId.get(s[3]);if(b!==undefined&&E[b].g==='brief'&&E[b].h<0)E[b].h=e.i;}});});
  E.forEach(e=>{if(e.h>=0){if(!kids.has(e.h))kids.set(e.h,new Set([e.h]));kids.get(e.h).add(e.i);}});
  const jaren=E.map(e=>e.j),y0=Math.min(j.sinds||9999,...jaren),y1=Math.max(+(window.STAND||'2026').slice(0,4),...jaren);
  return {slug,j,E,n,nOpen,kids,y0,y1,totaal:E.length};
}
function staat(P){
  return STAAT[P.slug]||(STAAT[P.slug]={sel:null,mb:P.totaal<=GROOT,open:false,jaren:null,lim:{},draad:null,sprong:0,isOpen:false});
}
const pas=(S,e)=>{
  if(S.open&&e.x.st!==4)return false;
  if(S.sel)return S.sel.has(e.g);
  if(e.g==='brief'&&!S.mb)return e.x.stap==='afdoeningsvoorstel';
  return true;
};

/* ---------- opmaak ---------- */
const STIJL=`
.lijnbox{container-type:inline-size;margin-top:4px}
.lijnbox .lj-intro{margin:0 0 12px;max-width:72ch;color:var(--sub)}
.lijnbox .lj-laad{padding:12px 0}
.lj-sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.lj-strook{display:grid;grid-auto-flow:column;grid-auto-columns:minmax(0,1fr);gap:4px;margin:8px 0 4px}
.lj-sj{font:inherit;color:var(--zwart);background:var(--grijs);border:1px solid var(--lijn);border-radius:6px;padding:6px 2px 4px;display:grid;justify-items:center;gap:0;cursor:pointer;min-width:0}
.lj-sj:hover:not(:disabled){border-color:var(--zwart)}
.lj-sj:disabled{cursor:default;opacity:.55}
.lj-sj svg{width:100%;max-width:60px;height:auto;display:block}
.lj-sj .jr{font-size:13px;font-weight:700;line-height:1.2}
.lj-sj .tt{font-size:12px;color:var(--sub);line-height:1.2}
.lj-br{fill:var(--blauw)}.lj-bc{fill:var(--groen)}.lj-as{stroke:var(--lijn);stroke-width:1}
.lj-leg{margin:0 0 14px;font-size:13px;color:var(--sub)}
.lj-leg b{font-weight:700}.lj-leg .r{color:var(--blauw)}.lj-leg .c{color:var(--groen-d)}
.lj-fil{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 6px;align-items:center}
.lj-chip{font:14px var(--font);color:var(--zwart);border:1px solid var(--lijn);background:var(--wit);border-radius:999px;padding:5px 12px 5px 9px;min-height:36px;cursor:pointer;display:inline-flex;gap:6px;align-items:center}
.lj-chip:hover{border-color:var(--zwart)}
.lj-chip[aria-pressed="true"]{background:var(--zwart);color:var(--wit);border-color:var(--zwart)}
.lj-chip svg{width:15px;height:15px;flex:none}
.lj-chip .n{font-variant-numeric:tabular-nums;opacity:.8}
.lj-chip.sw{padding-left:12px;border-style:dashed}
.lj-chip.sw[aria-pressed="true"]{background:var(--groen-zacht);color:var(--zwart);border:2px solid var(--groen);border-style:solid;padding:4px 11px}
.lj-hint{margin:6px 0 0;font-size:14px;color:var(--sub)}
.lj-link{font:inherit;color:var(--zwart);background:none;border:0;padding:4px 2px;text-decoration:underline;text-underline-offset:3px;cursor:pointer}
.lj-jaren,.lj-ev{list-style:none;margin:0;padding:0}
.lj-jaren{position:relative;margin-top:14px}
.lj-pre{position:relative;margin-top:10px}
.lj-jaren::before,.lj-pre::before{content:'';position:absolute;top:0;bottom:0;left:50%;width:3px;margin-left:-1.5px;background:var(--lijn);border-radius:2px}
.lj-kop{display:grid;grid-template-columns:minmax(0,1fr) 56px minmax(0,1fr);margin:0 0 8px;position:relative;z-index:2;font-size:13px;font-weight:700}
.lj-kop span:first-child{text-align:right;color:var(--blauw);padding-right:6px}.lj-kop span:last-child{color:var(--groen-d);padding-left:6px}
.lj-kop span{background:none}
.lj-jk{margin:0;display:flex;justify-content:center;position:relative;z-index:2;padding:6px 0 10px;font-size:16px}
.lj-jb{font:15px var(--font);cursor:pointer;display:inline-flex;gap:8px;align-items:baseline;border-radius:999px;padding:6px 16px;min-height:36px;background:var(--zwart);color:var(--wit);border:2px solid var(--zwart)}
.lj-jb b{font-weight:700;font-size:16px}
.lj-jb:not(.on){background:var(--wit);color:var(--zwart)}
.lj-jb:hover{border-color:var(--groen)}
.lj-jb span,.lj-jb i{font-style:normal;font-size:13px}
.lj-e{display:grid;grid-template-columns:minmax(0,1fr) 56px minmax(0,1fr);position:relative}
.lj-k{grid-row:1;min-width:0;background:var(--grijs);border:1px solid var(--lijn);border-radius:8px;padding:8px 12px;margin:0 0 10px}
.lj-e.r .lj-k{grid-column:1;text-align:right;border-right:4px solid var(--blauw)}
.lj-e.c .lj-k{grid-column:3;border-left:4px solid var(--groen)}
.lj-kn{grid-row:1;grid-column:2;position:relative;display:flex;justify-content:center;padding-top:6px;z-index:1}
.lj-nd{position:relative;z-index:1;width:30px;height:30px;border-radius:50%;background:var(--wit);display:grid;place-items:center}
.lj-e.r .lj-kn{color:var(--blauw)}.lj-e.c .lj-kn{color:var(--groen)}
.lj-kn::before{content:'';position:absolute;top:21px;height:3px;width:50%}
.lj-e.r .lj-kn::before{right:50%;background:var(--blauw)}.lj-e.c .lj-kn::before{left:50%;background:var(--groen)}
.lj-sv{width:22px;height:22px;display:block;fill:currentColor;stroke:currentColor;stroke-width:1.6;stroke-linejoin:round}
.lj-e.opn .lj-nd .lj-sv{fill:var(--wit)}
.lj-m{display:flex;flex-wrap:wrap;gap:2px 10px;align-items:center;font-size:13px;color:var(--sub)}
.lj-e.r .lj-m,.lj-e.r .lj-act{justify-content:flex-end}
.lj-lb{display:inline-flex;gap:5px;align-items:center;font-weight:700}
.lj-lb .lj-sv{width:14px;height:14px;stroke-width:1.8}
.lj-e.r .lj-lb{color:var(--blauw)}.lj-e.c .lj-lb{color:var(--groen-d)}
.lj-e.opn .lj-lb .lj-sv{fill:var(--wit)}
.lj-kl{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.lj-t{display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;margin:3px 0 0;font-size:15px;line-height:1.35;overflow-wrap:anywhere}
.lj-s{margin:3px 0 0;font-size:13px;color:var(--sub)}
.lj-st{margin:3px 0 0;font-size:13px}
.lj-act{display:flex;flex-wrap:wrap;gap:6px 12px;align-items:center;margin-top:6px;font-size:13px}
.lj-b{font:14px var(--font);color:var(--zwart);border:1px solid var(--zwart);background:var(--wit);border-radius:999px;padding:4px 12px;min-height:32px;cursor:pointer}
.lj-b:hover{background:var(--grijs)}
.lj-mk{font-size:12px;font-weight:700;border:1px solid currentColor;border-radius:4px;padding:0 5px}
.lj-e.dr .lj-k{background:var(--groen-zacht);box-shadow:0 0 0 2px var(--zwart)}
.lj-e.hf .lj-k{box-shadow:0 0 0 3px var(--zwart)}
.lj-d{margin-top:8px;padding-top:8px;border-top:1px solid var(--lijn);text-align:left;font-size:14px}
.lj-d h4{margin:0 0 4px;font-size:15px}
.lj-d p{margin:6px 0 0}
.lijnbox .spoor{list-style:none;margin:6px 0 0;padding:0 0 0 4px}
.lijnbox .spoor li{position:relative;padding:0 0 8px 20px;display:grid;grid-template-columns:7.5em minmax(0,1fr);gap:8px;font-size:14px}
.lijnbox .spoor li::before{content:'';position:absolute;left:0;top:5px;width:10px;height:10px;border-radius:50%;background:var(--wit);border:2px solid var(--sub)}
.lijnbox .spoor li:not(:last-child)::after{content:'';position:absolute;left:5px;top:17px;bottom:-3px;width:2px;background:var(--grijs2)}
.lijnbox .spoor li.z::before{border-color:var(--zwart);background:var(--zwart)}
.lijnbox .spoor li.m::before{border-color:var(--blauw);background:var(--blauw)}
.lijnbox .spoor li.k::before{border-color:var(--groen);background:var(--groen)}
.lijnbox .spoor li.o::before{border-color:var(--open);border-style:dashed}
.lijnbox .spoor li.l::before{border-color:var(--laat);background:var(--laat)}
.lijnbox .spoor .dt{color:var(--sub)}
.lj-lmw{display:flex;justify-content:center;position:relative;z-index:2;padding:0 0 12px}
.lj-lmw .lj-b{background:var(--wit)}
.lj-leeg{margin:12px 0;padding:12px 16px;background:var(--grijs);border-radius:8px}
.lj-uitleg{margin:14px 0 0;font-size:13px;color:var(--sub);max-width:80ch}
.lj-tg{margin-top:12px;display:flex;justify-content:center}
.lj-afk{margin:0 0 8px;font-size:14px;color:var(--sub)}
@container (max-width:640px){
  .lj-jaren::before,.lj-pre::before{left:14px}
  .lj-kop{display:none}
  .lj-jk{justify-content:flex-start}
  .lj-e{grid-template-columns:30px minmax(0,1fr)}
  .lj-e .lj-kn{grid-column:1;justify-content:flex-start}
  .lj-e.r .lj-k,.lj-e.c .lj-k{grid-column:2;text-align:left;border-right:1px solid var(--lijn);border-left:4px solid var(--groen);margin-left:6px}
  .lj-e.r .lj-k{border-left-color:var(--blauw)}
  .lj-e.r .lj-kn::before,.lj-e.c .lj-kn::before{left:50%;right:auto;width:50%}
  .lj-e.r .lj-m,.lj-e.r .lj-act,.lj-e .lj-m,.lj-e .lj-act{justify-content:flex-start}
  .lj-kl{position:static;width:auto;height:auto;overflow:visible;clip:auto;font-size:12px;font-weight:700;border:1px solid currentColor;border-radius:999px;padding:0 7px}
  .lj-e.r .lj-kl{color:var(--blauw)}.lj-e.c .lj-kl{color:var(--groen-d)}
  .lijnbox .spoor li{grid-template-columns:minmax(0,1fr)}
  .lj-nd{width:28px;height:28px}
}
@media (prefers-reduced-motion:reduce){.lijnbox *{transition:none!important;animation:none!important}}
`;
const SPRITE=`<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>
<symbol id="ljs-debat" viewBox="0 0 20 20"><circle cx="10" cy="10" r="7"/></symbol>
<symbol id="ljs-motie" viewBox="0 0 20 20"><rect x="3.5" y="3.5" width="13" height="13" rx="2"/></symbol>
<symbol id="ljs-vragen" viewBox="0 0 20 20"><path d="M3 4.5h14L10 17z"/></symbol>
<symbol id="ljs-wijk" viewBox="0 0 20 20"><path d="M10 2l7 4v8l-7 4-7-4V6z"/></symbol>
<symbol id="ljs-rapport" viewBox="0 0 20 20"><path d="M10 1.8l2.4 5.5 6 .6-4.5 4 1.4 5.9L10 14.7l-5.3 3.1 1.4-5.9-4.5-4 6-.6z"/></symbol>
<symbol id="ljs-toez" viewBox="0 0 20 20"><path d="M10 3l8 14H2z"/></symbol>
<symbol id="ljs-brief" viewBox="0 0 20 20"><rect x="2" y="5" width="16" height="10" rx="2"/></symbol>
<symbol id="ljs-voorstel" viewBox="0 0 20 20"><path d="M10 2l8 8-8 8-8-8z"/></symbol>
<symbol id="ljs-besluit" viewBox="0 0 20 20"><path d="M7 2.5h6l4.5 4.5v6L13 17.5H7L2.5 13V7z"/></symbol>
<symbol id="ljs-afd" viewBox="0 0 20 20"><circle cx="10" cy="10" r="7.5"/><path d="M6.3 10.2l2.5 2.6 5-5.4" style="fill:none;stroke:var(--wit);stroke-width:2.2"/></symbol></defs></svg>`;
function inject(){
  if(!document.getElementById('lijn-css')){const s=document.createElement('style');s.id='lijn-css';s.textContent=STIJL;document.head.appendChild(s);}
  if(!document.getElementById('lijn-sprite'))document.body.insertAdjacentHTML('afterbegin',`<div id="lijn-sprite" hidden>${SPRITE}</div>`);
}
const ico=s=>`<svg class="lj-sv" aria-hidden="true" focusable="false"><use href="#ljs-${s}"/></svg>`;

/* status met woorden (zelfde conventie als keten.js: .stip open/laat/af) */
function status(e){
  const x=e.x;
  if(x.st===4){const st=x.stap||[],l=st[st.length-1],vw=l&&l[1]==='verwacht'?l[0]:x.vw;
    if(vw)return vw<STAND?{k:'laat',t:`${dagen(vw,STAND)} dagen over de termijn`}:{k:'open',t:'Afdoening verwacht '+fd(vw)};
    return {k:'open',t:'Open'};}
  if(x.st===5){const st=x.stap||[],l=st[st.length-1],af=x.af||(l&&l[1]==='afgedaan'?l[0]:'');return {k:'af',t:'Afgedaan'+(af?' op '+fd(af):'')};}
  return null;
}
const subTekst=e=>(e.t==='toez'&&(e.x.st===4||e.x.st===5))?e.su.split(' · ')[0]:e.su;
function stappen(e){
  if(e.x.stap&&e.x.stap.length)return e.x.stap;
  const a=e.t==='toez'?['toegezegd','Toezegging gedaan']:['ingediend',(e.t==='amendement'?'Amendement':'Motie')+' ingediend'],r=[[e.d,a[0],a[1],'']];
  if(e.t!=='toez'){const w=(e.su.split(' · ')[1]||'').trim();
    if(e.x.st===2)r.push([e.d,'stemming',w?w.charAt(0).toUpperCase()+w.slice(1):'Verworpen','']);
    else if(e.x.st===3)r.push([e.d,'stemming','Ingetrokken of aangehouden','']);}
  return r;
}
function spoor(e){
  const ol=stappen(e).map((s,i)=>{
    const laat=s[1]==='verwacht'&&s[0]<STAND,k={ingediend:'z',stemming:'z',toegezegd:'z',tussenbericht:'m',commissieadvies:'m',afdoeningsvoorstel:'m',afgedaan:'k',verwacht:laat?'l':'o'}[s[1]]||'m';
    const u=s[3]?ITEM+s[3]:(i===0?e.u:''),t=u?`<a href="${esc(u)}" target="_blank" rel="noopener">${esc(s[2])}</a>`:esc(s[2]);
    return `<li class="${k}"><span class="dt">${fd(s[0])}</span><span>${t}${laat?` <b>(${dagen(s[0],STAND)} dagen over de termijn)</b>`:''}</span></li>`;}).join('');
  return `<ol class="spoor">${ol}</ol>`;
}

/* ---------- tekenen ---------- */
function zichtbaar(P,S){
  const rel=S.draad?P.kids.get(S.draad.h):null;
  return {vis:P.E.filter(e=>pas(S,e)||(rel&&rel.has(e.i))),rel};
}
function strook(P,vis){
  const A={};for(let y=P.y0;y<=P.y1;y++)A[y]=[[0,0],[0,0],[0,0],[0,0]];
  vis.forEach(e=>{if(A[e.j])A[e.j][e.q][e.k==='r'?0:1]++;});
  let mx=1;Object.values(A).forEach(q=>q.forEach(([r,c])=>{mx=Math.max(mx,r,c);}));
  const bt=Object.entries(A).map(([y,q])=>{
    const r=q.reduce((a,b)=>a+b[0],0),c=q.reduce((a,b)=>a+b[1],0);
    const bars=q.map(([a,b],i)=>{const x=1.5+i*11,ha=a?Math.max(2.5,a/mx*33):0,hb=b?Math.max(2.5,b/mx*33):0;
      return (ha?`<rect class="lj-br" x="${x}" y="${35-ha}" width="8" height="${ha}" rx="1"/>`:'')+(hb?`<rect class="lj-bc" x="${x}" y="37" width="8" height="${hb}" rx="1"/>`:'');}).join('');
    return `<button type="button" class="lj-sj" data-jr="${y}" data-fk="s:${y}" ${r+c?'':'disabled'} title="${y}: ${r} van de raad, ${c} van het college" aria-label="Ga naar ${y}: ${r} gebeurtenissen van de raad, ${c} van het college"><svg viewBox="0 0 47 72" aria-hidden="true" focusable="false"><line class="lj-as" x1="0" x2="47" y1="36" y2="36"/>${bars}</svg><span class="jr">${y}</span><span class="tt">${nf(r+c)}</span></button>`;}).join('');
  return `<div class="lj-strook" role="group" aria-label="Overzicht per jaar: klik om naar een jaar te springen">${bt}</div>
    <p class="lj-leg"><b class="r">Boven de lijn de raad</b>, <b class="c">eronder het college</b>; een balkje is een kwartaal. Klik op een jaar om erheen te springen.</p>`;
}
function evHTML(P,S,e,pre,rel){
  const T=TYPE[e.t]||TYPE.brief,opn=e.x.st===4,st=status(e),inD=rel&&rel.has(e.i),hf=S.draad&&S.draad.h===e.i;
  let act='';
  if(e.t==='debat'&&e.x.v&&e.x.s!=null)act+=`<button type="button" class="lj-b" data-lv="${e.i}" data-fk="v:${e.i}" aria-label="Bekijk dit debat in beeld: ${esc(e.ti)}">▶ Bekijk</button>`;
  if(e.t==='debat')act+=`<a href="${esc(e.u)}" target="_blank" rel="noopener">Agenda in iBabs</a>`;
  if(!pre&&e.h>=0&&(e.g!=='motie'||e.x.st===4||e.x.st===5||(e.x.stap&&e.x.stap.length))){const ak=S.draad&&S.draad.anker===e.i;
    act+=`<button type="button" class="lj-b" data-ld="${e.h}" data-an="${e.i}" data-fk="d:${e.i}" aria-expanded="${!!ak}" aria-controls="lj-d-${P.slug}-${e.i}">${ak?'Verberg het spoor':'Toon het spoor'}</button>`;
  }
  let det='';
  if(!pre&&S.draad&&S.draad.anker===e.i){
    const h=P.E[S.draad.h],kids=P.kids.get(h.i)||new Set(),n=kids.size-1,verb=[...kids].filter(i=>!pas(S,P.E[i])).length,s2=status(h);
    det=`<div class="lj-d" id="lj-d-${P.slug}-${e.i}"><h4>Spoor van ${h.t==='toez'?'de toezegging':h.t==='amendement'?'het amendement':'de motie'} ‘${esc(h.ti)}’</h4>${s2?`<div class="lj-st"><span class="stip ${s2.k}"></span>${esc(s2.t)}</div>`:''}${spoor(h)}
      <p class="sub">${n?`${n} andere gebeurtenis${n===1?'':'sen'} op de lijn horen erbij en zijn gemarkeerd${verb?`; ${verb} daarvan staan er alleen vanwege dit spoor, je filter zou ze verbergen`:''}.`:'Er zijn geen andere gebeurtenissen op de lijn aan gekoppeld.'}</p>
      <p class="sub"><a href="${esc(h.u)}" target="_blank" rel="noopener">Open in iBabs</a></p></div>`;}
  return `<li class="lj-e ${e.k} t-${e.t}${opn?' opn':''}${inD?' dr':''}${hf?' hf':''}" data-i="${e.i}"><span class="lj-kn" aria-hidden="true"><span class="lj-nd">${ico(T.s)}</span></span>
    <div class="lj-k"><div class="lj-m"><span class="lj-lb">${ico(T.s)}${T.l}</span><span class="lj-kl">${e.k==='r'?'raad':'college'}</span><time datetime="${e.d}">${fd(e.d)}</time>${inD&&!pre&&!hf?'<span class="lj-mk">in het spoor</span>':''}</div>
    <a class="lj-t" href="${esc(e.u)}" target="_blank" rel="noopener" title="${esc(e.ti)}">${esc(e.ti)}</a>
    ${subTekst(e)?`<p class="lj-s">${esc(subTekst(e))}</p>`:''}${st?`<p class="lj-st"><span class="stip ${st.k}"></span>${esc(st.t)}</p>`:''}
    ${act?`<div class="lj-act">${act}</div>`:''}${det}</div></li>`;
}
function uitleg(P){
  const j=P.j,soort=j.soort;
  const wat=soort==='onderwerp'||soort==='thema'
    ?'Een debat of stuk hoort erbij als het onderwerp in de titel staat of er vaak in wordt genoemd. Er kan dus iets tussen staan dat er maar zijdelings over gaat.'
    :'Een debat of stuk hoort erbij als het bij dit '+(soort==='domein'?'domein':soort==='gebied'?'gebied':'domein en gebied')+' is ingedeeld, op beleidsveld en op genoemde wijken en straten. Er kan dus iets tussen staan dat er maar zijdelings over gaat.';
  return `<p class="lj-uitleg">De tijdlijn bestaat uit debatten in raad en commissies, moties en amendementen, schriftelijke vragen, rapporten en wijkraadstukken (links) en toezeggingen, brieven, voorstellen, besluiten en afdoeningen van het college (rechts), sinds ${P.y0}. ${wat} Bron: iBabs en de raadssite, stand ${fd(j.stand||STAND)}.</p>`;
}
function filters(P,S){
  const alles=!S.sel&&S.mb&&!S.open&&P.totaal>0;
  const chips=GROEPEN.filter(([g])=>P.n[g]).map(([g,t,sym])=>{
    const aan=S.sel?S.sel.has(g):(g!=='brief'||S.mb);
    return `<button type="button" class="lj-chip" data-fc="${g}" data-fk="c:${g}" aria-pressed="${aan}"${g==='motie'?' title="Moties en amendementen"':''}>${ico(sym)}<span>${t}</span> <span class="n">(${nf(P.n[g])})</span></button>`;}).join('');
  const bl=P.n.brief||0,verborgen=S.sel||S.mb?0:P.E.filter(e=>e.g==='brief'&&e.x.stap!=='afdoeningsvoorstel').length;
  const hint=!S.sel&&bl&&P.totaal>GROOT?(S.mb?`<p class="lj-hint">Alle ${nf(bl)} brieven staan erbij · <button type="button" class="lj-link" data-fb="1" data-fk="b">verberg</button></p>`
      :`<p class="lj-hint">${nf(verborgen)} brieven verborgen (alleen de afdoeningsvoorstellen bij moties en toezeggingen staan erbij) · <button type="button" class="lj-link" data-fb="1" data-fk="b">toon</button></p>`):'';
  return `<div class="lj-fil" role="group" aria-label="Wat staat er op de lijn?"><button type="button" class="lj-chip" data-fa="1" data-fk="c:alles" aria-pressed="${alles}"><span>Alles</span> <span class="n">(${nf(P.totaal)})</span></button>${chips}
    ${P.nOpen?`<button type="button" class="lj-chip sw" data-fo="1" data-fk="o" aria-pressed="${S.open}"><span>Alleen wat nog openstaat</span> <span class="n">(${nf(P.nOpen)})</span></button>`:''}</div>${hint}`;
}
function teken(host){
  const o=host._lj;if(!o)return;const {P,S,opts}=o,act=document.activeElement,fk=act&&host.contains(act)?act.getAttribute('data-fk'):null;
  const ref=fk?host.querySelector(`[data-fk="${CSS_ESC(fk)}"]`):null,top0=ref?ref.getBoundingClientRect().top:0;
  const {vis,rel}=zichtbaar(P,S),open=S.isOpen;
  let h=opts.intro!==false&&open?`<p class="lj-intro">Eén lijn door de tijd. Links wat de raad zegt en vraagt, rechts wat het college belooft, stuurt en afdoet.</p>`:'';
  if(P.j.afgekapt)h+=`<p class="lj-afk">Alleen de nieuwste 1.500 gebeurtenissen sinds ${P.j.sinds||2022}.</p>`;
  h+=strook(P,vis);
  if(!open){
    const pre=vis.slice(0,3);
    h+=pre.length?`<ol class="lj-ev lj-pre" aria-label="De nieuwste gebeurtenissen">${pre.map(e=>evHTML(P,S,e,true,null)).join('')}</ol>`:'<p class="lj-leeg">Geen gebeurtenissen.</p>';
    if(opts.toggle!==false)h+=`<div class="lj-tg"><button type="button" class="knop wit klein" data-tg="1" data-fk="t" aria-expanded="false">Toon de hele tijdlijn (${nf(P.totaal)} gebeurtenissen)</button></div>`;
  }else{
    h+=filters(P,S);
    const per=new Map();vis.forEach(e=>{if(!per.has(e.j))per.set(e.j,[]);per.get(e.j).push(e);});
    const jaren=[...per.keys()].sort((a,b)=>b-a);
    if(!S.jaren||![...S.jaren].some(y=>per.has(y))){S.jaren=new Set();let t=0;for(const y of jaren){S.jaren.add(y);t+=per.get(y).length;if(t>=30)break;}}
    if(rel)rel.forEach(i=>{S.jaren.add(P.E[i].j);});
    if(S.sprong&&per.has(S.sprong))S.jaren.add(S.sprong);
    h+=jaren.length?`<div class="lj-kop" aria-hidden="true"><span>De raad</span><span></span><span>Het college</span></div><ol class="lj-jaren">${jaren.map(y=>{
      const l=per.get(y),op=S.jaren.has(y);let lim=S.lim[y]||LIM;
      if(op&&rel)l.forEach((e,k)=>{if(rel.has(e.i)&&k+1>lim)lim=Math.ceil((k+1)/LIM)*LIM;});
      const kop=`<h3 class="lj-jk"><button type="button" class="lj-jb${op?' on':''}" data-jk="${y}" data-fk="y:${y}" aria-expanded="${op}" aria-controls="lj-${P.slug}-${y}-l">${op?`<b>${y}</b><span>${nf(l.length)} gebeurtenissen</span><i aria-hidden="true">▴</i>`:`Toon <b>${y}</b> <span>(${nf(l.length)})</span><i aria-hidden="true">▾</i>`}</button></h3>`;
      return `<li class="lj-jaar" id="lj-${P.slug}-${y}">${kop}${op?`<ol class="lj-ev" id="lj-${P.slug}-${y}-l" aria-label="Gebeurtenissen in ${y}">${l.slice(0,lim).map(e=>evHTML(P,S,e,false,rel)).join('')}</ol>${l.length>lim?`<div class="lj-lmw"><button type="button" class="lj-b" data-lm="${y}" data-fk="m:${y}">Toon de volgende ${Math.min(LIM,l.length-lim)} van ${nf(l.length-lim)} in ${y}</button></div>`:''}`:''}</li>`;}).join('')}</ol>`
      :`<p class="lj-leeg">Niets bij deze keuze. <button type="button" class="lj-link" data-fa="1" data-fk="c:alles">Toon alles</button></p>`;
    if(opts.toggle!==false)h+=`<div class="lj-tg"><button type="button" class="knop wit klein" data-tg="1" data-fk="t" aria-expanded="true">Toon minder</button></div>`;
    h+=uitleg(P);
  }
  host.innerHTML=h;
  if(fk){const n=host.querySelector(`[data-fk="${CSS_ESC(fk)}"]`);if(n){n.focus({preventScroll:true});const d=n.getBoundingClientRect().top-top0;if(Math.abs(d)>1)window.scrollBy(0,d);}}
  if(S.sprong){const y=S.sprong;S.sprong=0;setTimeout(()=>{const t=document.getElementById(`lj-${P.slug}-${y}`);if(t){t.scrollIntoView({block:'start',behavior:reduced()?'auto':'smooth'});const b=t.querySelector('.lj-jb');if(b)b.focus({preventScroll:true});}},40);}
}
const CSS_ESC=s=>String(s).replace(/"/g,'\\"');

/* ---------- bediening ---------- */
function klik(host,ev){
  const o=host._lj;if(!o)return;const {P,S}=o,t=ev.target.closest('[data-fa],[data-fc],[data-fo],[data-fb],[data-jk],[data-jr],[data-lm],[data-ld],[data-lv],[data-tg]');
  if(!t||!host.contains(t))return;
  if(t.dataset.lv!==undefined){const e=P.E[+t.dataset.lv];W.rzLijnVideo(e.x.v,e.x.s,fd(e.d)+' · '+e.ti);return;}
  if(t.dataset.tg!==undefined){zet(host,!S.isOpen,true);return;}
  if(t.dataset.jr!==undefined){S.sprong=+t.dataset.jr;S.jaren=S.jaren||new Set();S.jaren.add(+t.dataset.jr);if(!S.isOpen){zet(host,true,true);return;}}
  else if(t.dataset.fa!==undefined){S.sel=null;S.mb=true;S.open=false;}
  else if(t.dataset.fc){const g=t.dataset.fc;if(!S.sel)S.sel=new Set([g]);else{if(S.sel.has(g))S.sel.delete(g);else S.sel.add(g);if(!S.sel.size)S.sel=null;}}
  else if(t.dataset.fo!==undefined)S.open=!S.open;
  else if(t.dataset.fb!==undefined)S.mb=!S.mb;
  else if(t.dataset.jk){const y=+t.dataset.jk;S.jaren=S.jaren||new Set();if(S.jaren.has(y))S.jaren.delete(y);else S.jaren.add(y);}
  else if(t.dataset.lm){const y=+t.dataset.lm;S.lim[y]=(S.lim[y]||LIM)+LIM;}
  else if(t.dataset.ld){const h=+t.dataset.ld,an=+t.dataset.an;S.draad=S.draad&&S.draad.anker===an?null:{h,anker:an};}
  teken(host);
}
function zet(host,open,meld){
  const o=host._lj;if(!o)return;o.S.isOpen=!!open;teken(host);
  if(meld&&o.opts.onToggle)o.opts.onToggle(!!open);
}
function rzLijn(host,slug,opts){
  opts=opts||{};inject();
  const wrap=opts.wrap;
  const start=P=>{
    if(wrap)wrap.hidden=false;
    const S=staat(P);S.isOpen=!!opts.open;
    host._lj={P,S,opts};
    if(!host._ljBound){host._ljBound=true;host.addEventListener('click',ev=>klik(host,ev));}
    host.classList.add('lijnbox');teken(host);
    if(opts.scroll)setTimeout(()=>(wrap||host).scrollIntoView({block:'start',behavior:'auto'}),80);
  };
  host.classList.add('lijnbox');
  if(CACHE[slug]){start(CACHE[slug]);return;}
  rzLijnIndex().then(ix=>{
    if(!ix[slug]){if(wrap)wrap.hidden=true;host.innerHTML='';return;}
    if(wrap)wrap.hidden=false;
    host.innerHTML='<p class="lj-laad sub">De tijdlijn wordt opgehaald…</p>';
    const doe=()=>rzLijnLaad(slug).then(P=>{if(host.isConnected)start(P);}).catch(()=>{host.innerHTML='<p class="lj-laad sub">De tijdlijn kon niet worden geladen.</p>';});
    if(opts.open||!('IntersectionObserver' in window)){doe();return;}
    const io=new IntersectionObserver(l=>{if(l.some(x=>x.isIntersecting)){io.disconnect();doe();}},{rootMargin:'400px 0px'});io.observe(host);
  });
}
function rzLijnZet(host,open,scrol){
  if(!host||!host._lj){return;}zet(host,open,false);if(scrol)host.scrollIntoView({block:'start'});
}
/* videovenster: kVideo staat in keten.js; die laden we alleen als er op ▶ wordt geklikt en hij er nog niet is */
let KP=null;
function rzLijnVideo(ref,sec,titel){
  if(typeof kVideo==='function'){kVideo(ref,sec,titel);return;}
  KP=KP||new Promise((ok,nok)=>{
    const l=document.createElement('link');l.rel='stylesheet';l.href=new URL('keten.css?v=7',BASE_URL()).href;document.head.appendChild(l);
    const s=document.createElement('script');s.src=new URL('keten.js?v=14',BASE_URL()).href;s.onload=ok;s.onerror=nok;document.head.appendChild(s);});
  KP.then(()=>kVideo(ref,sec,titel)).catch(()=>{alert('Het videovenster kon niet worden geladen.');});
}
const BASE_URL=()=>BASIS;
const W=window;
W.rzLijnIndex=rzLijnIndex;W.rzLijnAantal=rzLijnAantal;W.rzLijnLaad=rzLijnLaad;W.rzLijn=rzLijn;W.rzLijnZet=rzLijnZet;W.rzLijnVideo=rzLijnVideo;
})();
