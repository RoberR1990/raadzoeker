/* Elders (17-10-2026): wat andere gemeenten over hetzelfde onderwerp vastlegden (regels uit CVDR) en welke moties er
   werden ingediend (Open Raadsinformatie). Geen AI, geen ranglijst, geen oordeel: neutraal naast elkaar, met bron.
   Data: d/elders/index.json ({slug: aantal gemeenten}) en d/elders/<slug>.json (src/elders.py).
   Publiek:
     rzEldersIndex()           belofte van {slug: aantal}; zonder bestand {}
     rzEldersAantal(slug)      aantal gemeenten (0 = geen blok), pas na rzEldersIndex()
     rzElders(el, slug, opties) tekent in el. Opties: open (alles tonen, standaard dicht = per gemeente één regel),
                               wrap (element dat zichtbaar wordt zodra er gegevens zijn) */
(function(){
'use strict';
const BASIS=(document.currentScript&&document.currentScript.src)||location.href;
const e=s=>String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const MND=['jan','feb','mrt','apr','mei','jun','jul','aug','sep','okt','nov','dec'];
const fd=d=>d&&d.length>=10?`${+d.slice(8,10)} ${MND[+d.slice(5,7)-1]} ${d.slice(0,4)}`:(d||'');
const nl=n=>Number(n).toLocaleString('nl-NL');
let IDX=null;const CACHE={};
/* beta.js wordt door kop() geladen; hier even op wachten (max. 3 s) zodat label en uitleg bij het eerste tekenen al kloppen */
function betaKlaar(){return new Promise(ok=>{let n=0;const t=setInterval(()=>{if(window.rzBetaLaad||++n>30){clearInterval(t);(window.rzBetaLaad?rzBetaLaad():Promise.resolve()).then(ok,ok);}},100);});}
function rzEldersIndex(){return IDX||(IDX=Promise.all([fetch(new URL('d/elders/index.json',BASIS)).then(r=>r.ok?r.json():{}).catch(()=>({})),betaKlaar()])
  .then(([x])=>(window.__eldIx=(window.rzBetaActief&&!rzBetaActief('elders'))?{}:x)));}   // staat 'elders' in beta.json op 'uit', dan verdwijnt het blok
function rzEldersAantal(s){return (window.__eldIx&&window.__eldIx[s])||0;}
function laad(s){return CACHE[s]||(CACHE[s]=fetch(new URL('d/elders/'+s+'.json',BASIS)).then(r=>{if(!r.ok)throw 0;return r.json();}));}

function regel(r){return `<li><a href="${e(r.url)}" target="_blank" rel="noopener">${e(r.titel)}</a> <span class="sub">${r.in_werking?'geldt sinds '+fd(r.in_werking):''}${r.soort?' · '+e(r.soort):''}</span></li>`;}
function motie(m){return `<li><span class="sub num">${fd(m.datum)}</span> ${m.soort==='amendement'?'<span class="sub">amendement</span> ':''}<a href="${e(m.url)}" target="_blank" rel="noopener">${e(m.titel)}</a>${m.indieners?` <span class="sub">(${e(m.indieners)})</span>`:''}${m.uitslag?` <span class="sub">· ${e(m.uitslag)}</span>`:''}${m.uit_tekst?` <span class="sub" title="Het onderwerp staat niet in de titel maar in het verzoek van de motie">· onderwerp uit het verzoek</span>`:''}</li>`;}
const EERST=10;   // moties direct zichtbaar per gemeente; de rest achter 'Toon alle'
function gemeente(g){
  const M=g.moties,nm=M.length,nr=g.regels.length;
  const kop=`${nr?`${nr} ${nr===1?'regeling':'regelingen'}`:'geen regeling gevonden'} · ${nm?`${nl(nm)} ${nm===1?'motie':'moties'} sinds ${g.sinds||2022}`:'geen moties gevonden'}`;
  return `<details class="elg"><summary><b>${e(g.naam)}</b> <span class="sub">${kop}</span></summary>
    ${nr?`<h4>Geldende regels</h4><ul>${g.regels.map(regel).join('')}</ul>`:''}
    ${nm?`<h4>Moties en amendementen, nieuwste eerst</h4><ul>${M.slice(0,EERST).map(motie).join('')}</ul>${nm>EERST?`<ul class="elrest" hidden>${M.slice(EERST).map(motie).join('')}</ul><button type="button" class="beta-fb elmeer" data-n="${nl(nm)}">Toon alle ${nl(nm)}</button>`:''}`:''}
    ${g.uitslag?`<p class="sub">${e(g.uitslag)}</p>`:nm?`<p class="sub">${g.n_uitslag?`Bij ${nl(g.n_uitslag)} van de ${nl(nm)} staat de uitslag in het stuk zelf; bij de rest niet.`:'De uitslag staat niet in deze bron; zie het stuk zelf.'}</p>`:''}
    ${g.ris?`<p class="sub"><a href="${e(g.ris)}" target="_blank" rel="noopener">Raadsinformatie van ${e(g.naam)}</a></p>`:''}</details>`;
}
document.addEventListener('click',ev=>{const b=ev.target.closest('.elmeer');if(!b)return;const u=b.previousElementSibling;if(u){u.hidden=!u.hidden;b.textContent=u.hidden?`Toon alle ${b.dataset.n}`:'Toon minder';}});
async function rzElders(el,slug,o={}){
  if(!el)return;let d;try{d=await laad(slug);}catch(x){return;}
  if(!d||!d.gemeenten||!d.gemeenten.length)return;
  await betaKlaar();if(window.rzBetaActief&&!rzBetaActief('elders'))return;
  if(o.wrap){o.wrap.hidden=false;const h=o.wrap.querySelector('h2');if(h&&window.rzBetaBadge&&!h.querySelector('.beta-label'))h.insertAdjacentHTML('beforeend',rzBetaBadge('elders'));}
  el.innerHTML=(window.rzBetaBanner?rzBetaBanner('elders'):'')+`<p class="intro">Hoe andere gemeenten hetzelfde onderwerp regelen en welke moties hun raad behandelde. Ter vergelijking, zonder oordeel.</p>
    <div class="elders">${d.gemeenten.map(gemeente).join('')}</div>
    <p class="sub" style="margin-top:12px">Bronnen: <a href="https://lokaleregelgeving.overheid.nl" target="_blank" rel="noopener">overheid.nl, lokale regelgeving</a> ${d.stand_cvdr?`(stand ${fd(d.stand_cvdr)})`:''} en <a href="https://openbesluitvorming.nl" target="_blank" rel="noopener">Open Raadsinformatie</a> (vergaderingen tot ${fd(d.stand_ori)}). Moties zijn herkend aan hun naam en het onderwerp in de titel of het verzoek; er kunnen er ontbreken of te veel tussen staan. <a href="beta.html#elders">Meer uitleg</a></p>`;
}
window.rzEldersIndex=rzEldersIndex;window.rzEldersAantal=rzEldersAantal;window.rzElders=rzElders;
if(!document.getElementById('elders-css')){const s=document.createElement('style');s.id='elders-css';s.textContent=
`.elders{display:grid;gap:8px;margin-top:12px}.elg{border:1px solid var(--lijn,#d0d7dc);border-radius:4px;padding:8px 12px;background:var(--wit,#fff)}
.elg summary{cursor:pointer;display:flex;flex-wrap:wrap;gap:4px 12px;align-items:baseline}.elg h4{margin:12px 0 4px;font-size:15px}
.eltekst{margin-top:8px}.elg ul{margin:0;padding-left:18px}.elg li{margin:4px 0;font-size:15px}`;document.head.appendChild(s);}
})();
