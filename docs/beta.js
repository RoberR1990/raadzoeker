/* Beta-functies (17-10-2026). Eén register (beta.json) bepaalt welke functies als beta gelabeld zijn; pagina's vragen het hier op.
   Een functie live zetten als beta, later volwassen maken of weer uitzetten gaat dus door één regel in beta.json: status 'beta' (label
   overal), 'live' (label weg, uitlegpagina blijft) of 'uit' (functie verbergt zichzelf als ze rzBetaActief() gebruikt).
   Publiek:
     rzBetaLaad()           belofte van het register {id: {...}}; zonder bestand {}
     rzBetaStatus(id)       'beta' | 'live' | 'uit' | '' (pas na rzBetaLaad())
     rzBetaActief(id)       false alleen als de functie in het register op 'uit' staat (onbekend = actief)
     rzBetaBadge(id)        <span class="beta-label">beta</span> als de status 'beta' is, anders ''. Geen link: mag in een knop staan.
     rzBetaBanner(id)       balk met uitleg, link naar beta.html#id en een knop voor feedback; leeg als de status niet 'beta' is
   Knoppen met data-betafb="<id>" openen het feedbackformulier (rzFout). Gebruik: beta.html toont het hele register. */
(function(){
'use strict';
if(window.rzBetaLaad)return;   // al geladen (kop() en elders.js laden het allebei)
const BASIS=(document.currentScript&&document.currentScript.src)||location.href;
const e=s=>String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
let P=null,R={};
function rzBetaLaad(){return P||(P=fetch(new URL('beta.json',BASIS)).then(r=>r.ok?r.json():{}).catch(()=>({})).then(j=>(R=(j&&j.functies)||{})));}
const rzBetaStatus=id=>(R[id]&&R[id].status)||'';
const rzBetaActief=id=>rzBetaStatus(id)!=='uit';
const rzBetaBadge=id=>rzBetaStatus(id)==='beta'?'<span class="beta-label" title="Beta-functie: nieuw en nog experimenteel">beta</span>':'';
function rzBetaBanner(id){
  const f=R[id];if(!f||f.status!=='beta')return '';
  return `<div class="beta-balk" role="note"><span class="beta-label">beta</span><p><b>Nieuw en nog experimenteel.</b> ${e(f.waarom_beta_kort||'Dit is een beta-functie: het werkt, maar kan nog veranderen en is minder gecontroleerd dan de rest van de site.')}
    <a href="beta.html#${e(id)}">Wat is dit, en waarom deze gemeenten?</a> <button type="button" class="beta-fb" data-betafb="${e(id)}">Feedback of een wens</button></p></div>`;
}
document.addEventListener('click',ev=>{const b=ev.target.closest('[data-betafb]');if(!b||!window.rzFout)return;
  const f=R[b.dataset.betafb]||{};
  rzFout('Beta · '+(f.naam||b.dataset.betafb),{titel:'Feedback op een beta-functie',intro:f.feedback_vraag||'Wat werkt, wat mis je, wat klopt niet?',label:'Je feedback of wens'});});
if(!document.getElementById('beta-css')){const s=document.createElement('style');s.id='beta-css';s.textContent=
`.beta-label{display:inline-block;vertical-align:middle;font:700 12px/1 var(--font);color:var(--zwart);background:var(--open);border-radius:999px;padding:3px 9px;margin-left:8px;letter-spacing:.02em}
.beta-balk{display:flex;gap:10px;align-items:flex-start;background:var(--grijs);border-left:4px solid var(--open);border-radius:4px;padding:10px 14px;margin:0 0 12px}
.beta-balk .beta-label{margin:2px 0 0;flex:none}.beta-balk p{margin:0;font-size:15px;line-height:1.5}
.beta-fb{font:inherit;color:var(--groen);background:none;border:0;padding:0;text-decoration:underline;cursor:pointer}`;document.head.appendChild(s);}
window.rzBetaLaad=rzBetaLaad;window.rzBetaStatus=rzBetaStatus;window.rzBetaActief=rzBetaActief;window.rzBetaBadge=rzBetaBadge;window.rzBetaBanner=rzBetaBanner;
})();
