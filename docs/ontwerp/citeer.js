/* Citeren in één klik en 'Kopieer voor Copilot'. Zonder AI en zonder server: alles gebeurt in de browser.
   Geladen door kop() in ontwerp.js (net als stad.js); de pagina's wachten zo nodig op window.rzCiteerKlaar.
   Publieke functies (alle op window):
     rzKopieer(tekst|promise, melding)        klembord + terugval + melding; melding mag een functie zijn
     rzCiteer(o, sel)                          zet een citaat op het klembord (o mag een promise zijn)
     rzCitaatTekst(o, sel)                     alleen de tekst van het citaat
     rzVerwijzing(o) / rzVerwijzingTekst(o)    korte verwijzing naar een stuk
     rzCopilot({opdracht, intro, blokken, voet, max})   bouwt de Copilot-tekst (herbruikbaar, ook voor de tracker)
     rzCopilotKopieer(maker, {knop})           bouwt en kopieert (maker mag een promise opleveren)
     rzVoet(label, link, eenheid)              standaard voetregel met {n} en {totaal}
     rzTelRegel(t)                             telregel van tel.js als gewone zin
     rzVk / rzSleutelTekst / rzFragmentLink    vaste link naar een debatfragment (zoek.html#b=…); rzBasis = https://raadzoeker.nl/ontwerp/
     rzOrgaan(naam, bron), rzDatum(d), rzHms(s), rzSchoon(t), rzKort(t, n)
   Knoppen in de pagina's zijn gewone <button data-rzc="citaat|link|verw|copilot" data-rzb="<naam>" …>; ze worden gemaakt met
   citKnoppen() (ontwerp.js). Per naam levert de pagina een functie in window.RZ_CIT[naam](dataset, knop) die de gegevens teruggeeft. */
(()=>{
if(window.rzKopieer)return;

/* Copilot Chat accepteert maar een beperkte hoeveelheid tekst. 8.000 tekens is een voorzichtige grens; de echte limiet van
   Copilot Chat kan verschillen per licentie en per versie. Pas dit getal aan als dat blijkt. */
const RZ_COPILOT_MAX=8000;
const BASIS='https://raadzoeker.nl/ontwerp/';
const MNDL=['januari','februari','maart','april','mei','juni','juli','augustus','september','oktober','november','december'];
const slugje=s=>String(s||'').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/&/g,' ').replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
const rzDatum=d=>{const m=String(d||'').match(/^(\d{4})-(\d\d)-(\d\d)/);return m?`${+m[3]} ${MNDL[+m[2]-1]} ${m[1]}`:String(d||'');};
const rzHms=s=>{s=Math.max(0,Math.round(s));const h=Math.floor(s/3600),m=Math.floor(s%3600/60),z=s%60;return `${h}:${String(m).padStart(2,'0')}:${String(z).padStart(2,'0')}`;};
const rzSchoon=t=>String(t==null?'':t).replace(/\s+/g,' ').trim();
/* inkorten op een woordgrens */
const rzKort=(t,n)=>{t=rzSchoon(t);if(t.length<=n)return t;return t.slice(0,n-1).replace(/\s+\S*$/,'').replace(/[\s,;:.]+$/,'')+'…';};
const titelSchoon=t=>rzSchoon(t).replace(/[.\s]+$/,'');
/* 'Gemeenteraad' wordt gemeenteraad; 'Commissie Bouwen, Wonen en Buitenruimte (2022-2026)' wordt zonder haakjes */
const rzOrgaan=(naam,bron)=>{naam=rzSchoon(naam).replace(/\s*\([^)]*\)\s*$/,'');if(!naam)return bron?'raadscommissie':'gemeenteraad';
  return /^gemeenteraad$/i.test(naam)?'gemeenteraad':naam;};

/* ---------- melding (toast) en voorleesregio ---------- */
let LIVE=null;
function melding(t){
  if(!LIVE){LIVE=document.createElement('div');LIVE.className='rzc-live';LIVE.setAttribute('aria-live','polite');LIVE.setAttribute('role','status');document.body.appendChild(LIVE);}
  LIVE.textContent='';setTimeout(()=>{LIVE.textContent=t.replace(/<[^>]+>/g,'');},30);
  if(window.rzToast)window.rzToast(t,3200);
  else{let d=document.querySelector('.rzc-toast');if(!d){d=document.createElement('div');d.className='rzc-toast';document.body.appendChild(d);}
    d.textContent=t.replace(/<[^>]+>/g,'');d.hidden=false;clearTimeout(d._t);d._t=setTimeout(()=>{d.hidden=true;},3200);}
}
/* laatste redmiddel: de tekst in een venster tonen om met de hand te kopiëren */
function toonTekst(t){
  document.getElementById('rzc-dlg')?.remove();
  const d=document.createElement('div');d.id='rzc-dlg';d.setAttribute('role','dialog');d.setAttribute('aria-modal','true');d.setAttribute('aria-labelledby','rzc-dt');
  d.innerHTML='<div class="rzc-laag"></div><div class="rzc-vel"><h2 id="rzc-dt">Kopiëren lukte niet vanzelf</h2><p>Selecteer de tekst hieronder en kopieer hem met Ctrl+C (op een telefoon: lang indrukken).</p><textarea readonly rows="8"></textarea><div class="rzc-rij"><button type="button" class="knop">Sluiten</button></div></div>';
  document.body.appendChild(d);const ta=d.querySelector('textarea');ta.value=t;
  const weg=()=>{d.remove();};d.querySelector('.rzc-laag').onclick=weg;d.querySelector('button').onclick=weg;
  d.addEventListener('keydown',e=>{if(e.key==='Escape')weg();});
  ta.focus();ta.select();
}
function terugval(t,msg){
  const ta=document.createElement('textarea');ta.value=t;ta.setAttribute('readonly','');ta.style.cssText='position:fixed;top:0;left:0;opacity:0;';
  document.body.appendChild(ta);ta.select();ta.setSelectionRange(0,t.length);let ok=false;
  try{ok=document.execCommand('copy');}catch(e){}
  ta.remove();
  if(ok){melding(msg());return true;}
  toonTekst(t);melding('Kopiëren lukte niet vanzelf. De tekst staat in het venster.');return false;
}
/* tekst mag een string of een promise zijn. Bij een promise gebruiken we ClipboardItem, want Safari staat
   writeText na een await niet meer toe; met een ClipboardItem blijft het kopiëren aan het klikgebaar gekoppeld. */
function rzKopieer(tekst,mel){
  const msg=()=>{const m=typeof mel==='function'?mel():mel;return m||'Gekopieerd';};
  const isPromise=tekst&&typeof tekst.then==='function';
  const viaWrite=t=>{
    if(navigator.clipboard&&navigator.clipboard.writeText){return navigator.clipboard.writeText(t).then(()=>{melding(msg());return true;},()=>terugval(t,msg));}
    return Promise.resolve(terugval(t,msg));};
  if(!isPromise)return viaWrite(String(tekst));
  if(navigator.clipboard&&navigator.clipboard.write&&window.ClipboardItem){
    let laatste='';
    try{
      const item=new ClipboardItem({'text/plain':tekst.then(t=>{laatste=String(t);return new Blob([laatste],{type:'text/plain'});})});
      return navigator.clipboard.write([item]).then(()=>{melding(msg());return true;},()=>tekst.then(t=>viaWrite(String(t))));
    }catch(e){}
  }
  return tekst.then(t=>viaWrite(String(t)));
}

/* ---------- citaat ---------- */
/* o: {tekst, spreker, fractie, orgaan, herkomst, datum, punt, titel, auto, sec, bron, link}; sel = door de gebruiker geselecteerde tekst */
function rzCitaatTekst(o,sel){
  let t=rzSchoon(sel||o.tekst);
  if(sel)t=t.replace(/^…+\s*/,'').replace(/\s*…+$/,'');
  const wie=o.spreker?o.spreker+(o.fractie?' ('+o.fractie+')':''):'';
  let org='';
  if(o.orgaan)org=/rotterdam/i.test(o.orgaan)?o.orgaan:o.orgaan+' Rotterdam';else if(o.herkomst)org=o.herkomst;
  const titel=titelSchoon(o.titel);
  let punt='';
  if(o.punt||titel&&!o.herkomst)punt=(o.punt?'agendapunt '+o.punt:'agendapunt')+(titel?' ‘'+titel+'’':'');
  else if(titel)punt='‘'+titel+'’';
  const delen=[wie,org,o.datum?rzDatum(o.datum):'',punt,o.auto?'automatische ondertiteling (kan fouten bevatten)':'',o.sec!=null&&o.sec>=0?'video ca. '+rzHms(o.sec):''].filter(Boolean);
  const r=['‘'+t+'’'];
  if(delen.length)r.push('— '+delen.join(', '));
  if(o.bron)r.push('Bron: '+o.bron);
  if(o.link)r.push('Fragment: '+o.link);
  return r.join('\n');
}
/* kopieert een citaat; o mag een promise zijn (de selectie moet dan al bepaald zijn: geef sel mee) */
function rzCiteer(o,sel){return rzKopieer(Promise.resolve(o).then(x=>rzCitaatTekst(x,sel)),'Citaat gekopieerd');}
/* <Soort> ‘<titel>’, <wie>, <datum voluit>.\nBron: <url> */
function rzVerwijzingTekst(o){
  const k=[(o.soort?o.soort+' ':'')+'‘'+titelSchoon(o.titel)+'’'];if(o.wie)k.push(rzSchoon(o.wie));if(o.datum)k.push(rzDatum(o.datum));
  return k.join(', ')+'.'+(o.url?'\nBron: '+o.url:'');
}
const rzVerwijzing=o=>rzKopieer(Promise.resolve(o).then(rzVerwijzingTekst),'Verwijzing gekopieerd');

/* ---------- vaste link naar een debatfragment ---------- */
/* vergadering-deel van de sleutel: eerste 8 tekens van de agendaId, anders 'd' + datum zonder streepjes + r (raad) of c (commissie) */
const rzVk=(agendaId,datum,bron)=>agendaId?String(agendaId).slice(0,8):'d'+String(datum).replace(/-/g,'')+(bron?'c':'r');
/* sleutel in gewone tekst: <vk>~<agendapuntnr>~<slug(spreker)> */
const rzSleutelTekst=(vk,nr,spreker)=>vk+'~'+(nr||'')+'~'+(slugje(spreker)||'onbekende-spreker');
/* p: {vk, nr, spreker, t (videoseconde), s (nummer van het segment als er geen seconde is), n (2 of hoger als dezelfde sleutel vaker voorkomt)} */
function rzFragmentLink(p){
  let h='b='+encodeURIComponent(rzSleutelTekst(p.vk,p.nr,p.spreker));
  if(p.t!=null&&p.t>=0)h+='&t='+Math.round(p.t);else if(p.s)h+='&s='+p.s;
  if(p.n>1)h+='&n='+p.n;
  return BASIS+'zoek.html#'+h;
}
const rzDossierLink=slug=>BASIS+'dossier.html?d='+encodeURIComponent(slug);

/* ---------- Kopieer voor Copilot ---------- */
/* standaard voetregel; {n} en {totaal} worden ingevuld door rzCopilot */
const rzVoet=(label,link,eenheid)=>`Bron: Raadzoeker (raadzoeker.nl), onofficieel hulpmiddel op basis van openbare raadsinformatie. {n} van {totaal} ${eenheid||'fragmenten'}. ${label}: ${link}`;
/* o: {opdracht, intro (optioneel), totaal (optioneel), blokken:[{kop, tekst, bron, citaat}|{sectie}], voet, max}
   Een blok met `sectie` is een tussenkopje (niet genummerd). Blokken die er niet meer bij passen vallen af, van achteren naar voren.
   Resultaat: {tekst, n (aantal genummerde blokken), totaal, afgekapt} */
function rzCopilot(o){
  const max=o.max||RZ_COPILOT_MAX,blokken=o.blokken||[];
  const totaal=o.totaal||blokken.filter(b=>!b.sectie).length;   // o.totaal: het aantal beschikbare fragmenten, ook als er maar een deel wordt meegegeven
  const voet=(n)=>String(o.voet||'').replace('{n}',n).replace('{totaal}',totaal);
  const kop=[o.opdracht,o.intro].filter(Boolean).join('\n\n');
  const reserve=voet(totaal).length+2;
  let tekst=kop,n=0,afgekapt=false,wacht='';
  const bouw=(b,i,t)=>`[${i}] ${rzSchoon(b.kop)}`+(t?'\n'+(b.citaat?'‘'+t+'’':t):'')+(b.bron?'\nBron: '+b.bron:'');
  for(const b of blokken){
    if(b.sectie){wacht=rzSchoon(b.sectie)+':';continue;}
    const lead=wacht?wacht+'\n':'';
    let t=rzSchoon(b.tekst),s=bouw(b,n+1,t);
    const tot=tekst.length+2+lead.length+s.length+reserve;
    if(tot>max){
      const nieuw=t.length-(tot-max);   // zoveel tekens mag de tekst van dit blok nog hebben
      if(t&&nieuw>=250){t=rzKort(t,nieuw);s=bouw(b,n+1,t);afgekapt=true;}else{afgekapt=true;break;}
    }
    tekst+='\n\n'+lead+s;wacht='';n++;
    if(afgekapt)break;
  }
  if(!o.opdracht&&!o.intro)tekst=tekst.replace(/^\n+/,'');
  tekst+='\n\n'+voet(n);
  return {tekst,n,totaal,afgekapt};
}
/* maker: functie die {opdracht,…} oplevert of een promise daarvan. Toont 'Bezig…' op de knop zolang het duurt. */
function rzCopilotKopieer(maker,opt){
  opt=opt||{};const knop=opt.knop;let res=null;
  if(knop){if(knop.getAttribute('aria-disabled')==='true')return Promise.resolve(false);
    knop._label=knop.textContent;knop.setAttribute('aria-disabled','true');knop.setAttribute('aria-busy','true');knop.textContent='Bezig…';}
  const klaar=()=>{if(knop){knop.textContent=knop._label;knop.removeAttribute('aria-disabled');knop.removeAttribute('aria-busy');}};
  const p=Promise.resolve().then(maker).then(o=>{res=rzCopilot(o);if(!res.n)throw new Error('leeg');return res.tekst;});
  return rzKopieer(p,()=>`Gekopieerd: ${res.n} ${res.n===1?'fragment':'fragmenten'}. Plak dit in Copilot Chat.`)
    .then(ok=>{klaar();return ok;},()=>{klaar();melding('Er is niets om te kopiëren.');return false;});
}
/* telregel van tel.js (telling()) als gewone zin */
function rzTelRegel(t){
  const laat=n=>n?` (waarvan ${n} over de termijn)`:'',mt=n=>n+(n===1?' motie':' moties'),tz=n=>n+(n===1?' toezegging':' toezeggingen');
  return `Sinds ${t.sinds}: ${mt(t.aan)} aangenomen (${t.af} afgedaan); ${mt(t.mo)} in uitvoering${laat(t.mo_laat)}; ${tz(t.tz)} open${laat(t.tz_laat)}.`;
}

/* ---------- selectie en klikken ---------- */
/* alleen tekst die binnen een fragment ([data-rzfr]) van dezelfde kaart ([data-rzbox]) is geselecteerd telt */
function selTekst(knop){
  const box=knop.closest('[data-rzbox]');if(!box)return '';
  const s=window.getSelection&&getSelection();if(!s||s.isCollapsed||!s.rangeCount)return '';
  const r=s.getRangeAt(0),c=r.commonAncestorContainer,el=c.nodeType===1?c:c.parentElement;
  const fr=el&&el.closest('[data-rzfr]');
  if(!fr||!box.contains(fr))return '';
  return rzSchoon(s.toString());
}
let SNAP=null;
document.addEventListener('pointerdown',e=>{const b=e.target.closest&&e.target.closest('button[data-rzc]');SNAP=b?{b,t:selTekst(b),at:Date.now()}:null;},true);
document.addEventListener('click',e=>{
  const b=e.target.closest&&e.target.closest('button[data-rzc]');if(!b)return;
  if(b.getAttribute('aria-disabled')==='true')return;
  const fn=(window.RZ_CIT||{})[b.dataset.rzb];if(!fn)return;
  const sel=SNAP&&SNAP.b===b&&Date.now()-SNAP.at<2000?SNAP.t:selTekst(b);SNAP=null;
  const soort=b.dataset.rzc;
  const fout=()=>{melding('Dat lukte niet. Probeer het nog eens.');};
  let o;try{o=Promise.resolve(fn(b.dataset,b));}catch(x){fout();return;}
  if(soort==='citaat')rzKopieer(o.then(x=>rzCitaatTekst(x,sel)),'Citaat gekopieerd').catch(fout);
  else if(soort==='link')rzKopieer(o.then(x=>x.link),'Link gekopieerd').catch(fout);
  else if(soort==='verw')rzKopieer(o.then(rzVerwijzingTekst),'Verwijzing gekopieerd').catch(fout);
  else if(soort==='copilot')rzCopilotKopieer(()=>o,{knop:b});
});

/* ---------- opmaak ---------- */
const st=document.createElement('style');
st.textContent=`.rzc{font-family:var(--font,Arial)}.knop.rzc{padding:6px 14px;font-size:14px;min-height:36px}
.rzc[aria-disabled=true]{opacity:.65;cursor:progress}
.rzrij{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-top:8px}
#bub .rzrij{margin-top:10px}#bub .knop.rzc{background:transparent;color:var(--wit);border:2px solid var(--wit)}#bub .knop.rzc:hover{background:rgba(255,255,255,.18)}
#bub :focus-visible{outline:3px solid var(--wit);box-shadow:0 0 0 6px var(--zwart)}
.rzc-live{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}
.rzc-toast{position:fixed;left:50%;bottom:22px;transform:translateX(-50%);z-index:9700;background:#0F2A1A;color:#fff;border-radius:999px;padding:11px 20px;font:400 15px var(--font,Arial);max-width:calc(100vw - 24px);text-align:center}
html.kop-b .rzc-toast{bottom:calc(76px + env(safe-area-inset-bottom))}.rzc-toast[hidden]{display:none}
#rzc-dlg{position:fixed;inset:0;z-index:1000;display:flex;align-items:center;justify-content:center;padding:16px}
.rzc-laag{position:absolute;inset:0;background:rgba(0,25,12,.55)}
.rzc-vel{position:relative;background:var(--wit);color:var(--zwart);border-radius:10px;padding:22px 24px;max-width:560px;width:100%;box-shadow:0 10px 40px rgba(0,0,0,.3)}
.rzc-vel h2{margin:0 0 8px;font-size:21px}.rzc-vel p{margin:0 0 10px;font-size:15px}
.rzc-vel textarea{width:100%;box-sizing:border-box;font:14px/1.45 var(--font,Arial);padding:8px;border:1.5px solid var(--lijn);border-radius:6px;background:var(--wit);color:var(--zwart)}
.rzc-rij{display:flex;justify-content:flex-end;margin-top:10px}`;
document.head.appendChild(st);

Object.assign(window,{rzKopieer,rzCiteer,rzCitaatTekst,rzVerwijzing,rzVerwijzingTekst,rzCopilot,rzCopilotKopieer,rzVoet,rzTelRegel,
  rzVk,rzSleutelTekst,rzFragmentLink,rzDossierLink,rzBasis:BASIS,rzOrgaan,rzDatum,rzHms,rzSchoon,rzKort,RZ_COPILOT_MAX});
window.RZ_CIT=window.RZ_CIT||{};
})();
