/* Een beetje Rotterdam (5-10-2026): skyline-laadanimatie met havenkraan, Rotterdamse laadteksten en easter eggs.
   Geladen door kop() in ontwerp.js. De knipoog gaat over de stad, nooit over raadsleden, partijen of inwoners.
   - Elk element met alleen de tekst 'Laden…' (of data-laad="tekst") krijgt de skyline: Erasmusbrug, De Rotterdam, Euromast en een kraan die een container lost.
   - rzEi(zoekwoord): easter eggs bij bepaalde zoekwoorden (Zoeken en de Verkenner roepen dit aan).
   - Wie minder beweging wil (prefers-reduced-motion) krijgt alleen de tekst. */
(function(){
const RUSTIG=matchMedia('(prefers-reduced-motion: reduce)').matches;
const css=`
.rz-laad{display:flex;flex-direction:column;align-items:center;gap:6px;padding:28px 0;color:var(--sub,#3E4B50);font-size:15px}
.rz-laad svg{width:240px;max-width:70vw;height:auto;overflow:hidden}
.rz-laad.klein{flex-direction:row;padding:6px 0;gap:10px}.rz-laad.klein svg{width:110px}
.rz-laad .lijn{fill:none;stroke:currentColor;stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:420;stroke-dashoffset:420;animation:rzTeken 1.8s ease-out forwards}
.rz-laad .zacht{stroke-width:.8;opacity:.7}
.rz-laad .kat{animation:rzKat 3.2s ease-in-out infinite}
.rz-laad .doos{animation:rzDoos 3.2s ease-in-out infinite}
.rz-laad .boot{animation:rzBoot 7s linear infinite}
.rz-laad .golf{animation:rzGolf 2.4s ease-in-out infinite}
.rz-laad .sv{color:#00811F}
@keyframes rzTeken{to{stroke-dashoffset:0}}
@keyframes rzKat{0%,100%{transform:translateX(0)}45%,55%{transform:translateX(-22px)}}
@keyframes rzDoos{0%,100%{transform:translateY(0)}20%,80%{transform:translateY(-6px)}}
@keyframes rzBoot{from{transform:translateX(-30px)}to{transform:translateX(250px)}}
@keyframes rzGolf{0%,100%{transform:translateX(0)}50%{transform:translateX(-6px)}}
.rz-toast{position:fixed;left:50%;bottom:22px;transform:translateX(-50%);z-index:9700;background:#0F2A1A;color:#fff;border-radius:999px;padding:11px 20px;font:400 15px var(--font,Arial);box-shadow:0 10px 28px rgba(0,0,0,.3);max-width:calc(100vw - 24px);text-align:center;animation:rzIn .3s ease-out}
@keyframes rzIn{from{opacity:0;transform:translate(-50%,10px)}}
.rz-confetti{position:fixed;top:-12px;z-index:9690;width:9px;height:14px;pointer-events:none;animation:rzVal linear forwards}
@keyframes rzVal{to{transform:translateY(110vh) rotate(720deg)}}
.rz-golfbalk{position:fixed;left:0;right:0;bottom:-10px;height:70px;z-index:9690;pointer-events:none;animation:rzGolfIn 2.6s ease-in-out forwards}
@keyframes rzGolfIn{0%{transform:translateY(80px)}30%,70%{transform:translateY(0)}100%{transform:translateY(80px)}}
`;
const st=document.createElement('style');st.textContent=css;document.head.appendChild(st);

/* skyline: Erasmusbrug (met de knik in de pyloon: de Zwaan), De Rotterdam, Euromast, een containerkraan en een bootje op de Maas */
const SKY=`<svg viewBox="0 0 240 70" aria-hidden="true" class="sv">
  <path class="lijn" d="M0 58 H240"/>
  <path class="lijn" d="M24 50 H112"/><path class="lijn" d="M64 58 L67 42 L73 16"/>
  <path class="lijn zacht" d="M73 16 L34 50 M73 16 L44 50 M73 16 L54 50 M73 16 L84 50 M73 16 L96 50 M73 16 L108 50"/>
  <path class="lijn" d="M122 58 V30 H134 V22 H146 V34 H140 V58 M128 30 V24 H138"/>
  <path class="lijn" d="M168 58 V10 M164 26 H172 V30 H164 Z M168 10 V3"/>
  <g class="kat"><rect x="210" y="19" width="9" height="3" fill="currentColor"/><g class="doos"><path d="M214.5 22 v8" stroke="currentColor" stroke-width="1"/><rect x="208" y="30" width="13" height="7" rx="1" fill="currentColor" opacity=".85"/></g></g>
  <path class="lijn" d="M198 58 V20 M226 58 V20 M188 20 H236 M198 20 L206 12 L226 20 M206 12 V20"/>
  <g class="boot"><path class="lijn" d="M0 62 h14 l-3 4 h-8 z M5 62 v-4 h4 v4"/></g>
  <g class="golf"><path class="lijn zacht" d="M4 66 q6 -3 12 0 t12 0 t12 0 M130 67 q6 -3 12 0 t12 0"/></g>
</svg>`;
const ZIN=['Effe laden…','De kranen draaien al…','Container wordt gelost…','Nog effe, de brug staat open…','Niet lullen, laden…'];
window.rzLaad=(tekst,klein)=>`<div class="rz-laad${klein?' klein':''}" role="status">${RUSTIG?'':SKY}<span>${tekst||ZIN[Math.floor(Math.random()*ZIN.length)]}</span></div>`;
function vulLaders(root=document){
  root.querySelectorAll('[data-laad]').forEach(el=>{if(!el.dataset.gevuld){el.innerHTML=rzLaad(el.dataset.laad||'');el.dataset.gevuld=1;}});
  root.querySelectorAll('p,td,div').forEach(el=>{if(el.children.length)return;const t=el.textContent.trim();
    if(t==='Laden…')el.innerHTML=rzLaad('',el.tagName==='TD');
    else if(t==='De zoekindex wordt geladen…')el.innerHTML=rzLaad('Effe de zoekindex ophalen…',true);});
}

/* ---------- easter eggs ---------- */
function toast(t,ms=4200){document.querySelectorAll('.rz-toast').forEach(x=>x.remove());const d=document.createElement('div');d.className='rz-toast';d.setAttribute('role','status');d.innerHTML=t;document.body.appendChild(d);setTimeout(()=>d.remove(),ms);}
function confetti(kleuren){if(RUSTIG)return;for(let i=0;i<110;i++){const c=document.createElement('div');c.className='rz-confetti';const k=kleuren[i%kleuren.length];
  Object.assign(c.style,{left:Math.random()*100+'vw',background:k,border:k==='#fff'?'1px solid #ddd':'0',animationDuration:(1.8+Math.random()*1.8)+'s',animationDelay:Math.random()*.6+'s',borderRadius:Math.random()<.3?'50%':'2px'});
  document.body.appendChild(c);setTimeout(()=>c.remove(),4500);}}
function golf(){if(RUSTIG)return;const g=document.createElement('div');g.className='rz-golfbalk';
  g.innerHTML='<svg viewBox="0 0 1200 70" preserveAspectRatio="none" width="100%" height="70"><path d="M0 30 Q75 0 150 30 T300 30 T450 30 T600 30 T750 30 T900 30 T1050 30 T1200 30 V70 H0 Z" fill="#3B7FA8" opacity=".55"/><path d="M0 40 Q75 15 150 40 T300 40 T450 40 T600 40 T750 40 T900 40 T1050 40 T1200 40 V70 H0 Z" fill="#2A6489" opacity=".7"/></svg>';
  document.body.appendChild(g);setTimeout(()=>g.remove(),2700);}
/* kleine tekeningen voor de eieren */
const BRUG=`<svg viewBox="0 0 120 50" width="120" height="50" aria-hidden="true" style="color:#9BE07A;vertical-align:middle"><path d="M0 44H120" stroke="currentColor" fill="none" stroke-width="1.5"/>
  <path d="M10 36H62" stroke="currentColor" stroke-width="2"/><path d="M40 44 L42 32 L48 8" stroke="currentColor" fill="none" stroke-width="2"/><path d="M48 8 L16 36 M48 8 L26 36 M48 8 L56 36" stroke="currentColor" stroke-width=".8"/>
  <g style="transform-origin:80px 36px;transform-box:view-box;animation:rzKlap 2.4s ease-in-out 2 alternate"><path d="M80 36H110" stroke="currentColor" stroke-width="2"/></g><path d="M66 36H80" stroke="currentColor" stroke-width="2"/></svg>`;
const MAST=`<svg viewBox="0 0 40 60" width="34" height="52" aria-hidden="true" style="color:#9BE07A;vertical-align:middle;overflow:hidden"><path d="M0 58H40" stroke="currentColor"/>
  <g style="animation:rzMast 1.6s cubic-bezier(.2,.8,.2,1) both"><path d="M20 58V18M15 32H25V36H15Z" stroke="currentColor" fill="none" stroke-width="1.6"/><path d="M20 18V2" stroke="currentColor" stroke-width="1"/></g></svg>`;
const TRAM=`<svg viewBox="0 0 120 30" width="150" height="38" aria-hidden="true"><rect x="2" y="6" width="116" height="18" rx="5" fill="#fff" stroke="#00811F" stroke-width="2"/><rect x="2" y="17" width="116" height="7" fill="#00811F"/>
  ${[10,30,50,70,90].map(x=>`<rect x="${x}" y="9" width="14" height="6" rx="1" fill="#CFE7F2"/>`).join('')}<path d="M60 6 L66 0 M66 0 H74" stroke="#333" stroke-width="1.2"/><circle cx="22" cy="26" r="3" fill="#333"/><circle cx="98" cy="26" r="3" fill="#333"/></svg>`;
const st2=document.createElement('style');st2.textContent=`@keyframes rzKlap{from{transform:rotate(0)}to{transform:rotate(-55deg)}}@keyframes rzMast{from{transform:translateY(42px)}to{transform:translateY(0)}}
.rz-tram{position:fixed;z-index:9690;left:-170px;pointer-events:none;animation:rzRij 5.5s linear forwards}@keyframes rzRij{to{transform:translateX(calc(100vw + 200px))}}
.rz-zetels{position:fixed;z-index:9700;background:#0F2A1A;color:#fff;border-radius:999px;padding:4px 10px;font:700 13px var(--font,Arial);pointer-events:none}`;document.head.appendChild(st2);
function tram(){if(RUSTIG)return;const k=document.querySelector('header.balk');const r=k?k.getBoundingClientRect():{bottom:56};const t=document.createElement('div');t.className='rz-tram';t.style.top=Math.max(0,r.bottom-40)+'px';t.innerHTML=TRAM;document.body.appendChild(t);setTimeout(()=>t.remove(),5800);}
const EIEREN=[
  [/\berasmusbrug\b|\bde zwaan\b/i,()=>toast(`${RUSTIG?'':BRUG} De brug staat open. Even geduld, er vaart een schip door.`,5200)],
  [/\beuromast\b/i,()=>toast(`${RUSTIG?'':MAST} 185 meter. En dan nog de Space Tower erbij.`,4800)],
  [/\btram(lijn|lijnen|s)?\b|\bret\b/i,()=>{tram();toast('Instappen graag, de deuren sluiten. 🚋');}],
  [/\bkapsalon\b/i,()=>toast('Kapsalon: in 2003 uitgevonden in Rotterdam. Patat, shoarma, kaas en salade in één bakje. Ook de raad heeft het erover.')],
  [/\bfeijenoord\b/i,()=>toast('Feijenoord met ij is het gebied. Feyenoord met y is de club. Allebei van ons.')],
  [/\b(ge)?lul(len)?\b/i,()=>toast('Niet lullen maar poetsen. Hier: niet lullen maar zoeken.')],
  [/\b(feyenoord|de kuip)\b/i,()=>{confetti(['#E30613','#fff','#E30613','#fff','#111']);toast('Geen woorden maar daden. 🔴⚪');}],
  [/^\s*(010|rotterdam)\s*$/i,()=>toast('Rotterdam? Zo vaak genoemd dat we zijn gestopt met tellen. Niet verrassend.')],
  [/\bmaas\b/i,()=>{window.dispatchEvent(new CustomEvent('rz-ei',{detail:'maas'}));if(!document.getElementById('sg'))golf();toast('De Maas stroomt door alles heen. Ook door de raad.');}],
];
let laatste='';
window.rzEi=q=>{q=(q||'').trim();if(!q||q===laatste)return;laatste=q;for(const [rx,f] of EIEREN)if(rx.test(q)){f();break;}};
window.rzToast=toast;

function logoSpel(){
  if(!/startpagina/.test(location.pathname))return;const m=document.querySelector('header .merk');if(!m)return;let n=0,t;const z=[...m.querySelectorAll('svg circle')];
  m.addEventListener('click',e=>{e.preventDefault();n++;clearTimeout(t);t=setTimeout(()=>{n=0;z.forEach(c=>c.removeAttribute('style'));document.querySelector('.rz-zetels')?.remove();},4000);
    z.slice(0,9).forEach((c,i)=>{if(i<Math.round(n/23*9))c.setAttribute('style','fill:#9BE07A;opacity:1');});
    let b=document.querySelector('.rz-zetels');if(n>=3){if(!b){b=document.createElement('div');b.className='rz-zetels';document.body.appendChild(b);}const r=m.getBoundingClientRect();b.style.left=r.left+'px';b.style.top=(r.bottom+6)+'px';b.textContent=n+' van 45 zetels';}
    if(n===23){confetti(['#00811F','#fff','#9BE07A','#004C31']);toast('23 zetels: je hebt een meerderheid. Gefeliciteerd, dit is geen motie van wantrouwen.',6000);n=0;setTimeout(()=>{z.forEach(c=>c.removeAttribute('style'));document.querySelector('.rz-zetels')?.remove();},2500);}});}
const start=()=>{vulLaders();logoSpel();new MutationObserver(m=>{for(const r of m)for(const n of r.addedNodes)if(n.nodeType===1&&/Laden…|geladen…/.test(n.textContent||''))vulLaders(n.parentElement||document);}).observe(document.body,{childList:true,subtree:true});};
document.readyState==='loading'?addEventListener('DOMContentLoaded',start):start();
})();
