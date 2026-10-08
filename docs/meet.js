/* Meetlaag (Umami, 8-10-2026). Geladen door kop() in ontwerp.js. Zonder host en website-id (CONF) doet dit bestand niets.
   - rzMeet(naam, data): verstuurt een gebeurtenis; faalt nooit hardop. Tot de tracker geladen is, staat hij in een wachtrij.
   - Privacy by design: elke verzending gaat door rzMeetVoorVerzenden(): het pad is een 'virtueel pad' zonder zoekterm, hash of
     query (alleen utm_source/utm_medium/utm_campaign blijven), een referrer van de eigen site wordt teruggebracht tot het pad,
     de titel is het pad. Geen cookies. Zoektermen gaan niet naar Umami (die staan, anoniem, in de D1-zoeklog).
     Geen meting van personen of partijen: geen spreker- of fractiefilters, geen namen in gebeurtenissen.
   - Uitzetten: ?meet=uit (blijvend), ?meet=aan, Do Not Track, of localStorage 'umami.disabled'. ?meet=debug: alles naar de console
     en de tracker wordt niet geladen (rzMeet.log bevat de gebeurtenissen); ?meet=nodebug zet dat weer uit.
   - Gebeurtenissen en hoe je ze leest: ontwerp/meten.md. Installatie van Umami: nas/umami/README.md. */
(function(){
'use strict';
const CONF={
  host:'',                                   // bv. 'https://stats.raadzoeker.nl' of 'https://cloud.umami.is'; leeg = meetlaag uit
  id:'',                                     // website-id uit Umami (Instellingen > Websites)
  script:'script.js',                        // naam van het trackerbestand (alleen aanpassen als TRACKER_SCRIPT_NAME in Umami is gewijzigd)
  domeinen:'raadzoeker.nl',                  // alleen hier wordt gemeten (localhost en *.pages.dev tellen niet mee)
  waar:'op een eigen server van de maker'    // zin in de privacytekst op Over; aanpassen als je een andere host kiest
};
const LS={get(k){try{return localStorage.getItem(k);}catch(e){return null;}},set(k,v){try{localStorage.setItem(k,v);}catch(e){}},del(k){try{localStorage.removeItem(k);}catch(e){}}};

/* schakelaars via de link */
try{const m=new URLSearchParams(location.search).get('meet');
  if(m==='uit'){LS.set('rz-nometen','1');LS.set('umami.disabled','1');}
  else if(m==='aan'){LS.del('rz-nometen');LS.del('umami.disabled');}
  else if(m==='debug')LS.set('rz-meetdebug','1');
  else if(m==='nodebug')LS.del('rz-meetdebug');}catch(e){}

const DEBUG=LS.get('rz-meetdebug')==='1';
const DNT=navigator.doNotTrack==='1'||window.doNotTrack==='1';
const UIT=()=>LS.get('rz-nometen')==='1'||!!LS.get('umami.disabled')||DNT;
const CONF_OK=!!(CONF.host&&CONF.id);
const DOMEIN_OK=CONF.domeinen.split(',').includes(location.hostname);
const ACTIEF=CONF_OK&&DOMEIN_OK&&!UIT()&&!DEBUG;     // verstuurt echt
const LOG=[];

/* ---------- virtueel pad: wat Umami als 'pagina' ziet ---------- */
const SLUG=s=>String(s||'').toLowerCase().replace(/[^a-z0-9-]/g,'').slice(0,80);
const NAAM={index:'',startpagina:'',domeinen:'dossiers',zoek:'zoeken',lab:'inzichten'};
function pagina(pad){return (String(pad).split('/').pop()||'index.html').replace(/\.html$/,'')||'index';}
const PAG=pagina(location.pathname);
function pad(pathname,hash){
  const f=pagina(pathname),h=String(hash||'').replace(/^#/,'').split(/[\/&?=]/)[0];
  if(f==='dossier')return h?'/dossier/'+SLUG(h):'/dossiers';
  if(f==='briefing')return h?'/briefing/'+SLUG(h):'/briefing';
  if(f==='wijk'){if(/^w-/i.test(h))return '/wijk/'+SLUG(h.slice(2));return h?'/gebied/'+SLUG(h):'/gebieden';}
  return '/'+(f in NAAM?NAAM[f]:SLUG(f));
}
function utm(search){
  const p=new URLSearchParams(search||''),o=new URLSearchParams();
  for(const k of ['utm_source','utm_medium','utm_campaign']){const v=p.get(k);if(v)o.set(k,SLUG(v).slice(0,40));}
  const s=o.toString();return s?'?'+s:'';
}
const virtueel=()=>pad(location.pathname,location.hash)+utm(location.search);
const huidig=()=>pad(location.pathname,location.hash).split('/').pop();

/* ---------- gebeurtenissen ---------- */
const EMAIL=/[\w.+-]+@[\w-]+(\.[\w-]+)+/g,CIJFERS=/\d{7,}/g;
function schoon(d){
  const o={};let n=0;
  for(const k of Object.keys(d||{})){
    if(n>=12)break;let v=d[k];if(v===undefined||v===null)continue;
    if(typeof v==='number'){if(!isFinite(v))continue;v=Math.round(v*100)/100;}
    else if(typeof v!=='boolean'){v=String(v).replace(/\s+/g,' ').trim().replace(EMAIL,'[e-mail]').replace(CIJFERS,'[nr]').slice(0,100);if(!v)continue;}
    o[k.slice(0,30)]=v;n++;
  }
  return o;
}
const WACHT=[];let KLAAR=false;
function verstuur(naam,data){
  if(DEBUG){try{console.info('[meet]',naam,data);}catch(e){}LOG.push([naam,data]);return;}
  if(!KLAAR){if(WACHT.length<60)WACHT.push([naam,data]);return;}
  try{if(window.umami&&typeof window.umami.track==='function'){if(Object.keys(data).length)window.umami.track(naam,data);else window.umami.track(naam);}}catch(e){}
}
function rzMeet(naam,data){
  try{if(!(ACTIEF||DEBUG)||typeof naam!=='string'||!naam)return;verstuur(naam.slice(0,50),schoon(data));}catch(e){}
}
const SLIK=(window.rzMeet&&window.rzMeet.q)||[];     // gebeurtenissen van vóór het laden (stub in ontwerp.js)
window.rzMeet=rzMeet;
Object.assign(rzMeet,{
  actief:ACTIEF,log:LOG,pad,virtueel,schoon,
  uit(){LS.set('rz-nometen','1');LS.set('umami.disabled','1');},
  aan(){LS.del('rz-nometen');LS.del('umami.disabled');},
  uitgezet:UIT
});

/* Wat er daadwerkelijk de deur uitgaat: pad zonder zoekterm of hash; eigen referrer alleen als pad; titel = pad. Umami roept dit aan via data-before-send. */
window.rzMeetVoorVerzenden=function(type,payload){
  try{
    if(!payload||typeof payload!=='object')return payload;
    payload.url=virtueel();payload.title=pad(location.pathname,location.hash);
    if(payload.referrer){try{const u=new URL(payload.referrer);if(u.hostname===location.hostname)payload.referrer=u.origin+pad(u.pathname,'');}catch(e){payload.referrer='';}}
  }catch(e){}
  return payload;
};

/* ---------- paginaweergave (de site werkt met hash-routes, dus we sturen ze zelf) ---------- */
let LAATSTE=null;
function weergave(){
  const p=virtueel();if(p===LAATSTE)return;LAATSTE=p;
  if(DEBUG){try{console.info('[meet] pageview',p);}catch(e){}LOG.push(['pageview',p]);return;}
  if(!ACTIEF||!KLAAR)return;
  try{window.umami.track(x=>Object.assign({},x,{url:p,title:pad(location.pathname,location.hash)}));}catch(e){}
}
/* filters in de hash (Inzichten, Beloofd, Zoeken): alleen onderwerp-achtige sleutels; nooit zoekterm, spreker of fractie */
const WIT=['d','g','van','tot','k','tab','soort','domein','gebied','thema','onderwerp','status','blok','orde'];
let LAATSTE_F='',FT=0;
function filters(){
  if(!['lab','beloofd','zoek','vergaderingen'].includes(PAG))return;
  clearTimeout(FT);FT=setTimeout(()=>{
    try{const p=new URLSearchParams(location.hash.replace(/^#/,'')),o={pagina:PAG};let n=0;
      for(const k of WIT){const v=p.get(k);if(v){o[k]=v;n++;}}
      const s=JSON.stringify(o);if(!n||s===LAATSTE_F)return;LAATSTE_F=s;rzMeet('weergave',o);}catch(e){}
  },800);
}
addEventListener('hashchange',()=>{weergave();filters();});

/* ---------- klikken (op document, dus geen wijzigingen nodig in de pagina's) ---------- */
function groep(h){
  h=String(h).replace(/^www\./,'');
  if(/(^|\.)gemeenteraad\.rotterdam\.nl$/.test(h))return 'ibabs-raad';
  if(/(^|\.)wijkraad\.rotterdam\.nl$/.test(h))return 'ibabs-wijkraad';
  if(/companywebcast\.com$|connectlive\.ibabs\.eu$/.test(h))return 'video';
  if(/rekenkamer\.rotterdam\.nl$/.test(h))return 'rekenkamer';
  if(/(^|\.)overheid\.nl$|officielebekendmakingen\.nl$/.test(h))return 'overheid';
  if(/github\.com$/.test(h))return 'github';
  return h.slice(0,60);
}
const KLIK=[
  ['button[data-rzc]',el=>['kopieer',{soort:el.dataset.rzc,pagina:PAG}]],
  ['[data-tab]',el=>PAG==='zoek'?['zoek_tab',{tab:el.dataset.tab}]:null],
  ['button[data-video]',()=>['video',{pagina:PAG}]],
  ['[data-volg]',el=>{setTimeout(()=>rzMeet('volg',{slug:SLUG(el.dataset.volg),aan:el.getAttribute('aria-pressed')==='true'}),60);return null;}],
  ['#print',()=>PAG==='briefing'?['briefing',{actie:'pdf',slug:huidig()}]:null],
  ['#word',()=>PAG==='briefing'?['briefing',{actie:'word',slug:huidig()}]:null],
  ['#csv',()=>PAG==='beloofd'?['beloofd_csv',{}]:null],
  ['[data-kopieer]',el=>PAG==='lab'?['inzicht',{actie:'afbeelding',grafiek:el.dataset.kopieer}]:null],
  ['[data-link]',el=>PAG==='lab'?['inzicht',{actie:'link',grafiek:el.dataset.link}]:null],
  ['#verras,[data-a=verras]',()=>PAG==='verkenner'?['verkenner',{actie:'verras'}]:null],
  ['#route',()=>PAG==='verkenner'?['verkenner',{actie:'route'}]:null],
  ['#foto',()=>PAG==='verkenner'?['verkenner',{actie:'afbeelding'}]:null],
  ['[data-a=deel]',()=>PAG==='verkenner'?['verkenner',{actie:'deel'}]:null],
  ['a[href^="mailto:?subject"]',()=>['deel',{kanaal:'mail',pagina:PAG,slug:huidig()}]],
  ['a[href*="teams.microsoft.com/share"]',()=>['deel',{kanaal:'teams',pagina:PAG,slug:huidig()}]],
  ['a[href^="https://wa.me/"]',()=>['deel',{kanaal:'whatsapp',pagina:PAG,slug:huidig()}]],
  ['button.kopie',()=>['deel',{kanaal:'kopie',pagina:PAG,slug:huidig()}]],
  ['a[href]',el=>{
    let u;try{u=new URL(el.href,location.href);}catch(e){return null;}
    if(!/^https?:$/.test(u.protocol)||u.hostname===location.hostname)return null;
    if(/teams\.microsoft\.com$|^wa\.me$/.test(u.hostname))return null;     // telt al als 'deel'
    return ['uitgaand',{doel:groep(u.hostname),pagina:PAG}];}]
];
document.addEventListener('click',e=>{
  try{const t=e.target&&e.target.closest?e.target:null;if(!t)return;
    for(const [sel,fn] of KLIK){const el=t.closest(sel);if(!el)continue;const r=fn(el);if(r)rzMeet(r[0],r[1]);}}catch(x){}
},true);
document.addEventListener('toggle',e=>{
  try{const d=e.target;if(!d||d.tagName!=='DETAILS'||!d.open)return;
    if(d.hasAttribute('data-blok'))rzMeet('uitklap',{blok:d.getAttribute('data-blok'),slug:huidig()});
    else if(d.classList.contains('item'))rzMeet('resultaat_open',{pagina:PAG});}catch(x){}
},true);

/* ---------- privacytekst en keuze 'niet meetellen' op Over ---------- */
function privacy(){
  const li=document.getElementById('meetpriv');if(!li||!CONF_OK)return;
  const knop=()=>UIT()?'Weer meetellen':'Mijn bezoeken niet meetellen';
  li.innerHTML=`<b>Gebruik van de site:</b> we tellen anoniem welke pagina's en knoppen gebruikt worden (bijvoorbeeld kopiëren, delen en volgen) met het open-source programma Umami, ${CONF.waar}. Geen cookies, geen naam of e-mailadres, geen koppeling tussen je bezoeken. Zoektermen en wie of welke partij je bekijkt gaan hier niet naartoe; alleen of een zoekopdracht iets opleverde. ${DNT?'Je browser vraagt om niet gevolgd te worden; dat respecteren we.':`<button type="button" class="lk" id="meetknop">${knop()}</button>`}`;
  li.hidden=false;
  const kn=li.querySelector('#meetknop');
  if(kn)kn.onclick=()=>{if(UIT())rzMeet.aan();else rzMeet.uit();kn.textContent=knop();};
  const f=document.getElementById('meetfaq');if(f){f.textContent=' Daarnaast tellen we anoniem welke pagina\'s en knoppen worden gebruikt (zie Privacy hierboven).';f.hidden=false;}
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',privacy);else privacy();

/* ---------- tracker laden ---------- */
function laad(){
  const s=document.createElement('script');s.defer=true;s.src=CONF.host.replace(/\/+$/,'')+'/'+CONF.script;
  const d=s.dataset;
  d.websiteId=CONF.id;d.autoPageview='false';d.domains=CONF.domeinen;d.doNotTrack='true';
  d.excludeSearch='true';d.excludeHash='true';d.performance='true';d.beforeSend='rzMeetVoorVerzenden';
  s.onload=()=>{KLAAR=true;weergave();while(WACHT.length){const [n,x]=WACHT.shift();verstuur(n,x);}};
  s.onerror=()=>{WACHT.length=0;};
  document.head.appendChild(s);
}
if(ACTIEF)laad();
else if(DEBUG){KLAAR=true;weergave();}
SLIK.forEach(([n,x])=>rzMeet(n,x));
filters();
})();
