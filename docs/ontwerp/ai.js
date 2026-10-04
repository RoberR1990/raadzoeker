/* Gedeeld: AI-samenvatting met citaat-ballon en uitklapblokken (dossier.html, wijk.html). */
/* ---------- AI-samenvatting: zinnen met citaat als ballon ---------- */
let CIT=[];const reg=x=>CIT.push(x)-1;
const kort=(s,n)=>s.length>n?s.slice(0,n-1).replace(/\s+\S*$/,'')+'…':s;
const bron=x=>`<span class="bron">(<a href="${esc(x.url)}" target="_blank" rel="noopener">${esc(kort(x.bron_label||x.bron,90))}</a>, ${fd(x.bron_datum)})</span>`;
const cl=x=>`<button type="button" class="cl" data-c="${reg(x)}" aria-label="Toon letterlijk citaat">citaat</button>`;
const stand=x=>x.stand?`<span class="st">${esc(x.stand)}</span>`:'';
const zin=x=>`<span class="z" tabindex="0" data-c="${reg(x)}">${esc(x.zin)}</span>`;
const alinea=zs=>zs.map(zin).join(' ');
const rijAI=x=>`${esc(x.wat)}${stand(x)} ${bron(x)}${cl(x)}`;
function blok(id,titel,intro,inh,knop,label){
  return `<section class="vlak deel" id="${id}" aria-labelledby="${id}h"><h2 id="${id}h">${titel}${label?' <span class="ai">AI</span>':''}</h2>${intro}
    ${inh?`<button type="button" class="meerknop" aria-expanded="false" aria-controls="${id}i"><span class="tx">${knop}</span><span class="pijl" aria-hidden="true">▾</span></button><div class="inh" id="${id}i" hidden>${inh}</div>`:''}</section>`;
}
const BUB=document.createElement('div');BUB.id='bub';BUB.hidden=true;BUB.setAttribute('role','tooltip');document.body.appendChild(BUB);
let bubEl=null,bubVast=false;
function toonBub(el,vast){
  const x=CIT[+el.dataset.c];if(!x)return;
  if(bubEl)bubEl.classList.remove('aan');bubEl=el;bubVast=vast;el.classList.add('aan');
  BUB.innerHTML=`‘${esc(x.citaat)}’<span class="b">${x.auto?'automatische ondertiteling · ':''}<a href="${esc(x.url)}" target="_blank" rel="noopener">${esc(kort(x.bron_label||x.bron,90))}</a>, ${fd(x.bron_datum)}</span>`;
  BUB.hidden=false;const r=el.getBoundingClientRect(),w=BUB.offsetWidth;
  BUB.style.left=Math.max(16,Math.min(document.documentElement.clientWidth-w-16,r.left))+scrollX+'px';
  const boven=r.top-BUB.offsetHeight-8;BUB.style.top=(boven>8?boven:r.bottom+8)+scrollY+'px';
}
function verberg(){if(bubEl)bubEl.classList.remove('aan');bubEl=null;bubVast=false;BUB.hidden=true;}
document.addEventListener('mouseover',e=>{if(bubVast)return;const el=e.target.closest('[data-c]');if(el)toonBub(el,false);else if(!e.target.closest('#bub'))verberg();});
document.addEventListener('focusin',e=>{const el=e.target.closest('[data-c]');if(el&&!bubVast)toonBub(el,false);});
document.addEventListener('keydown',e=>{if(e.key==='Escape')verberg();});
document.addEventListener('click',e=>{
  const el=e.target.closest('[data-c]');
  if(el){e.preventDefault();if(bubEl===el&&bubVast)verberg();else toonBub(el,true);return;}
  if(!e.target.closest('#bub'))verberg();
  const k=e.target.closest('.meerknop');
  if(k){const open=k.getAttribute('aria-expanded')==='true',inh=document.getElementById(k.getAttribute('aria-controls')),tx=k.querySelector('.tx');
    k.setAttribute('aria-expanded',String(!open));inh.hidden=open;if(!k.dataset.t)k.dataset.t=tx.textContent;tx.textContent=open?k.dataset.t:'Minder tonen';
    if(open){const s=k.closest('section');if(s.getBoundingClientRect().top<0)s.scrollIntoView({block:'start'});}
    if(window.naUitklap)naUitklap();}
});

/* volledige AI-samenvatting als losse secties (voor de gebiedspagina) */
function aiSecties(A){
  const n=xs=>(xs||[]).length,T=A.tijdlijn||{},F=A.fracties||{},C=A.college||{},W=A.wijken||{},O=A.open||{};let h='';
  if(A.verdieping&&A.verdieping.length)h+=blok('av','Meer diepgang',`<p class="intro">${alinea(A.verdieping[0])}</p>`,A.verdieping.length>1?`<div class="verd">${A.verdieping.slice(1).map(a=>`<p>${alinea(a)}</p>`).join('')}</div>`:'','Lees verder',true);
  if(n(T.punten))h+=blok('at','Tijdlijn',`<p class="intro">${alinea(T.intro||[])}</p>`,`<div class="tlr">${T.punten.map(x=>`<div class="d">${fd(x.bron_datum)}</div><div class="pt">${rijAI(x)}</div>`).join('')}</div>`,`Toon ${n(T.punten)} momenten`,true);
  if(n(F.punten))h+=blok('af','Wat de fracties vinden',`<p class="intro">${alinea(F.intro||[])}</p>`,F.punten.map(f=>`<div class="pt"><b>${esc(f.fractie)}</b> ${f.standpunten.map(x=>`${esc(x.wat.replace(/\.$/,''))}${stand(x)} ${bron(x)}${cl(x)}`).join('; ')}</div>`).join(''),`Toon ${n(F.punten)} fracties`,true);
  if(n(C.punten))h+=blok('ac','Wat het college beloofde en deed',`<p class="intro">${alinea(C.intro||[])}</p>`,C.punten.map(x=>`<div class="pt">${rijAI(x)}</div>`).join(''),`Toon ${n(C.punten)} punten`,true);
  if(n(W.punten))h+=blok('aw','Signalen uit de wijken',`<p class="intro">${alinea(W.intro||[])}</p>`,W.punten.map(x=>`<div class="pt"><b>${esc(x.wijk)}</b> ${rijAI(x)}</div>`).join(''),`Toon ${n(W.punten)} signalen`,true);
  if(n(O.punten))h+=blok('ao','Open eindjes',`<p class="intro">${alinea(O.intro||[])}</p>`,O.punten.map(x=>`<div class="pt">${rijAI(x)}</div>`).join(''),`Toon ${n(O.punten)} punten`,true);
  return h;
}
