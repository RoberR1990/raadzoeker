/* Rondleiding voor nieuwe gebruikers (5-10-2026). Wordt door ontwerp.js op elke pagina geladen.
   - Eerste bezoek: welkomstvenster 'wil je een rondleiding?' (onthouden in localStorage, tot er accounts zijn).
   - Daarna, eerste keer op een andere pagina: klein balkje 'korte uitleg van deze pagina?'.
   - Altijd terug te vinden via de ?-knop in de kop (deze pagina, hele site, veelgestelde vragen, woordenlijst).
   - Een stap wijst een element aan (donkere laag met uitsparing) met een korte tekst; soms een knop 'laat een voorbeeld zien'.
   - ?tour=1 in de link start de rondleiding van die pagina (gebruikt door hulp.html). */
(function(){
const PAG=(location.pathname.split('/').pop()||'startpagina.html').replace('.html','')||'startpagina';
const LS={get:k=>{try{return localStorage.getItem('rz-'+k);}catch(e){return null;}},set:(k,v)=>{try{localStorage.setItem('rz-'+k,v);}catch(e){}}};
const css=`
.rzt-laag{position:fixed;inset:0;z-index:9998;background:transparent}
.rzt-spot{position:fixed;z-index:9999;border-radius:12px;box-shadow:0 0 0 3px #00811F,0 0 0 9999px rgba(0,25,12,.62);transition:all .28s cubic-bezier(.3,0,.2,1);pointer-events:none}
.rzt-spot.leeg{box-shadow:0 0 0 9999px rgba(0,25,12,.62);width:0!important;height:0!important;left:50%!important;top:45%!important}
.rzt-tip{position:fixed;z-index:10000;width:min(380px,calc(100vw - 32px));background:var(--wit);color:var(--zwart,#000);border-radius:14px;padding:18px 20px 14px;box-shadow:0 18px 50px rgba(0,0,0,.35);font:400 15px/1.5 var(--font,Arial);transition:top .28s,left .28s}
.rzt-tip h3{margin:0 0 6px;font-size:18px;line-height:1.25}
.rzt-tip p{margin:0 0 10px}
.rzt-tip .rzt-tel{font-size:12.5px;color:#3E4B50}
.rzt-tip .rzt-rij{display:flex;gap:8px;align-items:center;justify-content:space-between;margin-top:8px;flex-wrap:wrap}
.rzt-tip button,.rzt-welkom button,.rzt-balk button{font:700 14px var(--font,Arial);border-radius:999px;padding:9px 16px;cursor:pointer;border:2px solid #00811F;background:#00811F;color:#fff}
.rzt-tip button.wit,.rzt-welkom button.wit,.rzt-balk button.wit{background:var(--wit);color:#00811F}
.rzt-tip button.link,.rzt-welkom button.link,.rzt-balk button.link{border:0;background:none;color:#3E4B50;padding:9px 6px;font-weight:400;text-decoration:underline}
.rzt-tip .rzt-vb{display:inline-flex;gap:6px;align-items:center;margin:2px 0 6px;background:#E1EFE2;color:#004C31;border:0;font-weight:700}
.rzt-stip{display:flex;gap:5px}.rzt-stip i{width:7px;height:7px;border-radius:50%;background:#CAD6DA}.rzt-stip i.on{background:#00811F}
.rzt-welkom{position:fixed;z-index:10000;left:50%;top:50%;transform:translate(-50%,-50%);width:min(520px,calc(100vw - 32px));background:var(--wit);border-radius:18px;padding:28px 28px 22px;box-shadow:0 30px 80px rgba(0,0,0,.4);font:400 16px/1.55 var(--font,Arial)}
.rzt-welkom h2{margin:0 0 8px;font-size:26px}
.rzt-welkom ul{margin:10px 0 16px;padding-left:20px}.rzt-welkom li{margin:3px 0}
.rzt-welkom .rzt-rij{display:flex;gap:10px;flex-wrap:wrap;align-items:center}
.rzt-balk{position:fixed;z-index:9000;left:50%;bottom:18px;transform:translateX(-50%);background:var(--wit);border-radius:999px;padding:8px 8px 8px 18px;box-shadow:0 10px 30px rgba(0,0,0,.25);display:flex;gap:10px;align-items:center;font:400 14.5px var(--font,Arial);max-width:calc(100vw - 24px)}
.rzt-hulp{display:inline-flex;align-items:center;justify-content:center;width:30px;height:30px;border-radius:50%;border:2px solid #fff;background:transparent;color:#fff;font:700 16px var(--font,Arial);cursor:pointer;margin-left:6px;flex:none}
.rzt-hulp:hover{background:var(--wit);color:#00811F}
.rzt-menu{position:fixed;z-index:9500;background:var(--wit);color:var(--zwart,#000);border-radius:12px;box-shadow:0 14px 40px rgba(0,0,0,.25);padding:6px;min-width:250px;font:400 15px var(--font,Arial)}
.rzt-menu a,.rzt-menu button{display:block;width:100%;text-align:left;border:0;background:none;padding:10px 12px;border-radius:8px;color:var(--zwart,#000);text-decoration:none;font:inherit;cursor:pointer}
.rzt-menu a:hover,.rzt-menu button:hover{background:#E1EFE2}
@media (max-width:760px){.rzt-hulp{position:fixed;left:12px;bottom:12px;width:42px;height:42px;background:#00811F;border-color:#fff;z-index:8000;box-shadow:0 6px 18px rgba(0,0,0,.3)}}
@media (max-width:600px){.rzt-tip{left:16px!important;right:16px;bottom:16px;top:auto!important;width:auto}.rzt-balk{border-radius:14px;flex-wrap:wrap;justify-content:center;bottom:10px}}
`;
const st=document.createElement('style');st.textContent=css;document.head.appendChild(st);

/* ---------- de stappen ---------- */
const KOP=[
  {s:'header .merk',t:'Welkom bij raadzoeker',x:'Hier vind je wat de Rotterdamse gemeenteraad sinds 2018 zei, besloot en beloofde. Het logo brengt je altijd terug naar de startpagina.'},
  {s:'header nav a[href="zoek.html"]',t:'Zoeken',x:'Zoek in alles wat er in de raad en de commissies is gezegd en geschreven. Bij debatten spring je direct naar het moment in de video.'},
  {s:'header nav a[href="vergaderingen.html"]',t:'Vergaderingen',x:'Wat er in de raad en de commissies is besproken, samengevat in één minuut of uitgebreid, kort na de vergadering.'},
  {s:'header nav a[href="domeinen.html"]',t:'Domeinen',x:'Dossiers per beleidsveld en onderwerp: wat er is gezegd, besloten en beloofd, en wat ervan terechtkwam.'},
  {s:'header nav a[href="wijk.html"]',t:'Gebieden',x:'Kies een gebied of wijk: waar praat de raad over, wat vraagt de wijkraad, en een paar cijfers.'},
  {s:'header nav a[href="lab.html"]',t:'Inzichten',x:'Grafieken over wat de raad doet, om te kopiëren in je eigen presentatie.'},
  {s:'header nav a[href="verkenner.html"]',t:'Verkenner',x:'Alles als één web van begrippen. Om rond te dwalen en verbanden te ontdekken.'},
  {s:'#bijgewerkt',t:'Altijd actueel',x:'Hier zie je hoe vers de gegevens zijn. De site werkt zichzelf elke paar uur bij.'},
  {s:'.rzt-hulp',t:'Hulp nodig?',x:'Via dit vraagteken start je deze uitleg opnieuw, per pagina, en vind je de veelgestelde vragen en een woordenlijst.'},
];
const STAP={
  startpagina:[
    {s:'#zf',t:'Begin met zoeken',x:'Typ een onderwerp, wijk of woord. Je krijgt alles wat de raad erover zei, met de stukken erbij.',vb:['Probeer: parkeren',()=>location.href='zoek.html?q=parkeren']},
    {s:'#wolk',t:'Waar praat de raad over?',x:'De grootste woorden kregen dit jaar de meeste aandacht. Klik op een woord voor het dossier.'},
    {s:'#mat',t:'Domein × gebied',x:'Elke rij is een beleidsveld, elke kolom een gebied. Hoe donkerder, hoe meer er over die combinatie is gezegd en geschreven. Klik op een vakje.'},
    {s:'#recent',t:'Net besloten',x:'De nieuwste besluiten, moties en toezeggingen, met een link naar de officiële stukken.'},
    {s:'#belofte',t:'Beloftes',x:'Hoeveel moties en toezeggingen nog open staan of al zijn afgedaan.'},
  ],
  zoek:[
    {s:'#zf',t:'Zoek in alles',x:'Alle woorden moeten voorkomen. Zet woorden tussen "aanhalingstekens" voor een exacte zin.',vb:['Laat een voorbeeld zien',()=>{const q=document.getElementById('q');if(q){q.value='tramlijn 4';q.form.requestSubmit?q.form.requestSubmit():q.form.submit();}}]},
    {s:'#van',p:1,t:'Filters',x:'Beperk tot een periode, een domein of een gebied. De filters staan ook in de link, zodat je een zoekopdracht kunt delen.'},
    {s:'#analyse',t:'In één oogopslag',x:'Per jaar, per fractie, per gebied en de dossiers waar het over gaat. Fracties staan op alfabet.'},
    {s:'#tabs',t:'Gezegd of geschreven',x:'"Gezegd" zijn de debatten (met video), "Stukken" zijn moties, brieven, vragen en andere officiële documenten.'},
    {s:'#uit button[data-video]',alt:'#uit',t:'Bekijk het moment',x:'Met deze knop speelt de vergadering af vanaf het moment dat het werd gezegd. De tekst is soms automatisch ondertiteld; check bij twijfel de video.'},
  ],
  domeinen:[
    {s:'#uit',t:'Uitgelicht',x:'Voorbeelddossiers met het hele verhaal: van debat tot besluit, beloftes en wat er in de stad gebeurde.'},
    {s:'#ond',t:'Alle onderwerpen',x:'Per domein de onderwerpen. Een groen label betekent: er is een samenvatting (door AI gemaakt, met gecontroleerde citaten).'},
    {s:'#rijen',t:'Alles op een rij',x:'Per domein hoeveel moties en toezeggingen er open staan en hoeveel er over de termijn zijn.'},
  ],
  dossier:[
    {s:'.kopknoppen .knop',alt:'#dossier h1',t:'Briefing in één klik',x:'Maak van dit dossier een A4 voor je wethouder of overleg, als pdf of Word.'},
    {s:'.kverw',t:'Verder kijken',x:'De onderwerpen binnen dit dossier, verwante dossiers en hetzelfde dossier per gebied.'},
    {s:'#kinh .ai, #dossier .ai',t:'AI-samenvatting met bron',x:'Wijs een zin aan of tik erop: je ziet het letterlijke citaat en de bron. Elk citaat is woord voor woord gecontroleerd.'},
    {s:'#kinh .kblok',t:'Het verhaal in stappen',x:'Gezegd, besloten, beloofd, gedaan. Elk blok toont de 3 nieuwste punten; klik op de kop om het open te klappen.',vb:['Klap een blok open',()=>{const b=document.querySelector('#kinh .kblok:not(.open) .kkop');if(b)b.click();}]},
    {s:'#deelrij',t:'Delen',x:'Deel de link via e-mail, Teams of WhatsApp. Wie de link opent, komt precies hier uit.'},
  ],
  wijk:[
    {s:'#kaart',t:'Kies een gebied',x:'Klik op de kaart of kies uit de lijst.'},
    {s:'#ak',t:'In het kort',x:'Wat er in dit gebied speelt, als samenvatting met citaten. Wijs een zin aan voor de bron.'},
    {s:'#ow',t:'Waar praat de raad over?',x:'De onderwerpen per jaar als het over dit gebied gaat. Klik op een jaar of onderwerp.'},
    {s:'#wr',t:'De wijkraad',x:'Adviezen, wijkakkoorden en verslagen van de wijkraden in dit gebied.'},
  ],
  verkenner:[
    {s:'#sg',t:'Eén web van alles',x:'Elk bolletje is een begrip of onderwerp. Begrippen die vaak samen vallen, staan dicht bij elkaar. Scroll of knijp om te zoomen, wijs aan om verbanden te zien, klik voor details.'},
    {s:'#zk',t:'Zoek een begrip',x:'Typ een woord en de kaart vliegt ernaartoe.',vb:['Laat Parkeren zien',()=>{const z=document.getElementById('zk');z.value='Parkeren';z.dispatchEvent(new Event('change'));}]},
    {s:'#fg',t:'Bekijk door een bril',x:'Kies een gebied, domein, fractie of periode: je ziet dan het web dat daar het meest speelt.'},
    {s:'#speel',t:'Tijdmachine',x:'Speel 2018 tot nu af en zie onderwerpen opkomen en verdwijnen.'},
    {s:'#verr',t:'Ontdek',x:'Verrassende verbanden tussen domeinen, een route van het ene naar het andere begrip, of twee gebieden naast elkaar.'},
  ],
  lab:[
    {s:'#toc',t:'Grafieken',x:'Spring naar een grafiek: moties, toezeggingen, samenwerking tussen fracties en meer.'},
    {s:'#fd',p:1,t:'Filters',x:'Filter alle grafieken tegelijk op domein, gebied, fractie of periode.'},
    {s:'[data-kopieer]',t:'Kopieer als afbeelding',x:'Plak een grafiek direct in een presentatie of mail, met titel, filter, bron en link erbij.'},
    {s:'#g-wrapped',t:'Raad Wrapped',x:'Het jaar van de raad in deelbare kaarten.'},
  ],
  vergaderingen:[{s:'#hero',t:'De laatste raadsvergadering',x:'Wat de raad het laatst besprak, in één minuut. Klik door voor de uitgebreide versie met wat elke fractie zei.'},
    {s:'#komt',t:'Komt eraan',x:'Wat er de komende weken op de agenda staat. Klap een vergadering open: per onderwerp zie je de dossiers en wanneer het eerder besproken is.'},
    {s:'#cols',t:'Per commissie',x:'De laatste vergaderingen van elke commissie, met hun belangrijkste onderwerpen.'},
    {s:'#mstrip',t:'Archief per maand',x:'Kies een maand: de raad, de commissies en de besluiten van de wijkraden per gebied.'}],
  vergadering:[
    {s:'.schakel',t:'Kort of uitgebreid',x:'Kies de korte versie (1 minuut lezen) of de uitgebreide, met per onderwerp wat de fracties en het college zeiden.'},
    {s:'.kort .zin',t:'Tik voor de bron',x:'Tik op een zin: je ziet het letterlijke citaat en een knop naar dat moment in de video.'},
    {s:'.ap .apmeta',doe:()=>document.querySelector('.schakel [data-m=uitgebreid][aria-pressed=false]')?.click(),t:'Per onderwerp',x:'Hoe laat en hoe lang een onderwerp besproken is. Met ▶ kijk je dat stuk van de vergadering terug.'},
    {s:'.ap .pt',t:'Tik op een fractie',x:'Tik op een fractie of wethouder: je ziet wat er letterlijk is gezegd, met ▶ naar precies dat moment in de video.'},
    {s:'.ap .dch',t:'Meer hierover',x:'Links naar het dossier over dit onderwerp: wat de raad er eerder over zei, besloot en beloofde.'},
    {s:'.vkop .acties',t:'De hele vergadering',x:'Of bekijk de hele vergadering, de agenda en stukken in iBabs of de officiële besluitenlijst.'},
  ],
  ideeen:[{s:'#lijst',t:'Denk mee',x:'Stem op ideeën voor nieuwe functies (3 stemmen) of stel er zelf een voor.'}],
  akkoord:[{s:'#kern',t:'Het coalitieakkoord',x:'De kern van het akkoord, samengevat. Wijs een zin aan voor de letterlijke tekst en de pagina.'},{s:'#dom',t:'Per domein',x:'Wat het akkoord per domein van plan is, met een link naar het dossier.'}],
  briefing:[{s:'#a4',t:'Je briefing',x:'Een A4 met het belangrijkste uit het dossier.'},{s:'#print',t:'Exporteren',x:'Bewaar als pdf of open in Word en pas hem aan.'}],
};
const NAAM={vergaderingen:'Vergaderingen',vergadering:'deze vergadering',startpagina:'de startpagina',zoek:'Zoeken',domeinen:'Domeinen',dossier:'dit dossier',wijk:'Gebieden',verkenner:'de Verkenner',lab:'Inzichten',ideeen:'Ideeën',akkoord:'het akkoord',briefing:'de briefing'};

/* ---------- rondleiding ---------- */
let T=null;
function zichtbaar(el){if(!el)return false;const r=el.getBoundingClientRect();return r.width>0&&r.height>0&&getComputedStyle(el).visibility!=='hidden';}
function zoekEl(stap){for(const sel of [stap.s,stap.alt].filter(Boolean)){for(const el of document.querySelectorAll(sel)){const e=stap.p?el.parentElement:el;if(zichtbaar(e))return e;}}return null;}
async function wacht(stap,ms=2500){const t0=Date.now();let el;while(!(el=zoekEl(stap))&&Date.now()-t0<ms)await new Promise(r=>setTimeout(r,150));return el;}
function start(stappen){
  stop();T={stappen,i:0};
  T.laag=Object.assign(document.createElement('div'),{className:'rzt-laag'});T.laag.onclick=stop;
  T.spot=Object.assign(document.createElement('div'),{className:'rzt-spot leeg'});
  T.tip=Object.assign(document.createElement('div'),{className:'rzt-tip'});T.tip.setAttribute('role','dialog');T.tip.setAttribute('aria-live','polite');T.tip.tabIndex=-1;
  document.body.append(T.laag,T.spot,T.tip);
  addEventListener('keydown',toets);addEventListener('resize',plaats);addEventListener('scroll',plaats,true);
  toon(0,1);
}
function stop(){if(!T)return;[T.laag,T.spot,T.tip].forEach(x=>x.remove());removeEventListener('keydown',toets);removeEventListener('resize',plaats);removeEventListener('scroll',plaats,true);T=null;}
function toets(e){if(!T)return;if(e.key==='Escape')stop();else if(e.key==='ArrowRight')toon(T.i+1,1);else if(e.key==='ArrowLeft')toon(T.i-1,-1);}
async function toon(i,richting){
  if(!T)return;if(i<0)i=0;if(i>=T.stappen.length){stop();LS.set('tour-'+PAG,'ja');return;}
  const stap=T.stappen[i];if(stap.doe&&richting>0)try{stap.doe();}catch(e){}
  const el=stap.s?await wacht(stap,richting>0?2500:800):null;
  if(!T)return;
  if(stap.s&&!el){T.stappen.splice(i,1);return toon(i,richting);}   // element is er (nu) niet: stap overslaan
  T.i=i;T.el=el;
  if(el)el.scrollIntoView({block:'nearest',inline:'center'});   // ook horizontaal (menu op mobiel)
  const n=T.stappen.length;
  T.tip.innerHTML=`<div class="rzt-tel">${i+1} van ${n}</div><h3>${stap.t}</h3><p>${stap.x}</p>
    ${stap.vb?`<button type="button" class="rzt-vb">▶ ${stap.vb[0]}</button>`:''}
    <div class="rzt-rij"><div class="rzt-stip">${T.stappen.map((_,j)=>`<i class="${j===i?'on':''}"></i>`).join('')}</div>
    <div>${i>0?'<button type="button" class="wit" data-a="terug">Vorige</button> ':''}<button type="button" data-a="verder">${i===n-1?'Klaar':'Volgende'}</button></div></div>
    <div style="text-align:right"><button type="button" class="link" data-a="stop">Sluit de uitleg</button></div>`;
  T.tip.querySelector('[data-a=verder]').onclick=()=>toon(T.i+1,1);
  const tb=T.tip.querySelector('[data-a=terug]');if(tb)tb.onclick=()=>toon(T.i-1,-1);
  T.tip.querySelector('[data-a=stop]').onclick=()=>{LS.set('tour-'+PAG,'ja');stop();};
  const vb=T.tip.querySelector('.rzt-vb');if(vb)vb.onclick=()=>{const f=stap.vb[1];stop();f();};
  plaats();inBeeld(el);setTimeout(plaats,el?420:0);T.tip.focus({preventScroll:true});
}
/* zorg dat het aangewezen element zichtbaar is in het deel van het scherm dat de uitleg niet bedekt (op mobiel zit de uitleg onderin) */
function inBeeld(el){if(!el||!T)return;const r=el.getBoundingClientRect(),mob=innerWidth<=600,boven=64,onder=mob?innerHeight-T.tip.offsetHeight-28:innerHeight-24;
  const ruimte=onder-boven;let dy=0;
  if(mob&&!el.closest('header'))dy=r.top-90;               // telefoon: element altijd bovenin, ruim boven de uitleg
  else if(r.height>ruimte)dy=r.top-boven;                       // te groot: bovenkant in beeld
  else if(r.top<boven)dy=r.top-boven-(el.closest('header')?0:16);
  else if(r.bottom>onder)dy=r.bottom-onder;
  else if(!mob&&r.bottom+T.tip.offsetHeight+30>innerHeight&&r.top-T.tip.offsetHeight-30<0)dy=r.top-boven;
  if(Math.abs(dy)>4)scrollBy({top:dy,behavior:'smooth'});}
function plaats(){
  if(!T)return;const el=T.el,tip=T.tip;
  if(!el){T.spot.classList.add('leeg');tip.style.left=Math.max(16,(innerWidth-tip.offsetWidth)/2)+'px';tip.style.top=Math.max(16,(innerHeight-tip.offsetHeight)/2)+'px';return;}
  T.spot.classList.remove('leeg');const r=el.getBoundingClientRect(),m=6;
  const top=Math.max(4,r.top-m),h=Math.min(r.height+2*m,innerHeight-top-4);
  Object.assign(T.spot.style,{left:(r.left-m)+'px',top:top+'px',width:(r.width+2*m)+'px',height:h+'px'});
  if(innerWidth<=600)return;   // op de telefoon staat de uitleg onderin (css)
  const tw=tip.offsetWidth,th=tip.offsetHeight;let x,y;
  if(r.bottom+th+20<innerHeight){y=r.bottom+14;x=r.left;}
  else if(r.top-th-20>0){y=r.top-th-14;x=r.left;}
  else if(r.right+tw+20<innerWidth){x=r.right+14;y=Math.max(16,Math.min(r.top,innerHeight-th-16));}
  else if(r.left-tw-20>0){x=r.left-tw-14;y=Math.max(16,Math.min(r.top,innerHeight-th-16));}
  else{x=(innerWidth-tw)/2;y=innerHeight-th-16;}
  tip.style.left=Math.max(16,Math.min(x,innerWidth-tw-16))+'px';tip.style.top=y+'px';
}
const pagina=()=>STAP[PAG]||[];
function tourPagina(){start(pagina().length?pagina():KOP);}
function tourSite(){start(KOP.concat(pagina()));}

/* ---------- welkom, balkje, ?-knop ---------- */
function welkom(){
  const laag=Object.assign(document.createElement('div'),{className:'rzt-laag'});laag.style.background='rgba(0,25,12,.62)';
  const w=Object.assign(document.createElement('div'),{className:'rzt-welkom'});w.setAttribute('role','dialog');w.setAttribute('aria-labelledby','rzt-wt');
  w.innerHTML=`<h2 id="rzt-wt">Welkom bij raadzoeker</h2>
    <p>Alles wat de Rotterdamse gemeenteraad sinds 2018 zei, besloot en beloofde, op één plek:</p>
    <ul><li><b>Zoeken</b> in debatten en stukken, met het videomoment erbij</li><li><b>Dossiers</b> per onderwerp: van debat tot besluit en belofte</li><li><b>Gebieden</b>: wat speelt er in jouw wijk</li></ul>
    <p style="margin-bottom:18px">Zal ik je in een minuut laten zien hoe het werkt?</p>
    <div class="rzt-rij"><button type="button" data-a="ja">Ja, laat zien</button><button type="button" class="wit" data-a="later">Zelf rondkijken</button><button type="button" class="link" data-a="nee">Niet meer vragen</button></div>
    <p style="font-size:13px;color:#3E4B50;margin:14px 0 0">Je vindt de uitleg altijd terug onder het <b>?</b> rechtsboven.</p>`;
  const dicht=(k)=>{LS.set('welkom',k);laag.remove();w.remove();};
  w.querySelector('[data-a=ja]').onclick=()=>{dicht('ja');tourSite();};
  w.querySelector('[data-a=later]').onclick=()=>dicht('later');
  w.querySelector('[data-a=nee]').onclick=()=>dicht('nee');
  laag.onclick=()=>dicht('later');
  document.body.append(laag,w);w.querySelector('[data-a=ja]').focus();
}
function balkje(){
  const b=Object.assign(document.createElement('div'),{className:'rzt-balk'});b.setAttribute('role','status');
  b.innerHTML=`<span>Eerste keer op ${NAAM[PAG]||'deze pagina'}? Korte uitleg?</span><button type="button" data-a="ja">Laat zien</button><button type="button" class="link" data-a="nee" aria-label="Nee, dank je">Nee</button>`;
  const weg=()=>{LS.set('tour-'+PAG,'ja');b.remove();};
  b.querySelector('[data-a=ja]').onclick=()=>{weg();tourPagina();};b.querySelector('[data-a=nee]').onclick=weg;
  document.body.appendChild(b);setTimeout(()=>{if(b.isConnected)weg();},14000);
}
function hulpknop(){
  const nav=document.querySelector('header .kopknoppen')||document.querySelector('header .rechts');if(!nav||nav.querySelector('.rzt-hulp'))return;
  const k=Object.assign(document.createElement('button'),{type:'button',className:'rzt-hulp',textContent:'?',title:'Hulp en uitleg'});k.setAttribute('aria-label','Hulp en uitleg');k.setAttribute('aria-haspopup','menu');
  nav.insertBefore(k,nav.querySelector('.menuknop'));
  k.onclick=e=>{e.stopPropagation();const oud=document.querySelector('.rzt-menu');if(oud){oud.remove();return;}
    const m=Object.assign(document.createElement('div'),{className:'rzt-menu'});m.setAttribute('role','menu');
    m.innerHTML=`${pagina().length?`<button type="button" data-a="p">Uitleg van ${NAAM[PAG]||'deze pagina'}</button>`:''}<button type="button" data-a="s">Rondleiding door de site</button><a href="hulp.html#faq">Veelgestelde vragen</a><a href="hulp.html#woorden">Wat betekent… (woordenlijst)</a><button type="button" data-a="f">Fout melden</button><a href="hulp.html#contact">Vraag stellen</a>`;
    const r=k.getBoundingClientRect();document.body.appendChild(m);
    // onder de knop als daar plek is (kop), anders erboven (op mobiel staat de knop linksonder)
    if(r.bottom+8+m.offsetHeight<innerHeight)m.style.top=(r.bottom+8)+'px';else m.style.top=Math.max(8,r.top-8-m.offsetHeight)+'px';
    if(r.left<innerWidth/2)m.style.left=Math.max(8,r.left)+'px';else m.style.right=Math.max(8,innerWidth-r.right)+'px';
    m.onclick=ev=>{const a=ev.target.closest('[data-a]');if(!a)return;m.remove();a.dataset.a==='f'?window.rzFout&&rzFout(''):a.dataset.a==='p'?tourPagina():tourSite();};
    setTimeout(()=>addEventListener('click',function sl(){m.remove();removeEventListener('click',sl);}),0);};
}
/* '/' zet de cursor in de zoekbalk */
addEventListener('keydown',e=>{if(e.key!=='/'||/input|textarea|select/i.test(document.activeElement.tagName))return;const q=document.querySelector('#q,#zk,#zoek,#zf input');if(q){e.preventDefault();q.focus();}});

function init(){
  hulpknop();
  const p=new URLSearchParams(location.search);
  if(p.get('tour')){setTimeout(()=>p.get('tour')==='site'?tourSite():tourPagina(),600);return;}
  const w=LS.get('welkom');
  if(!w){setTimeout(welkom,900);return;}
  if(w!=='nee'&&pagina().length&&!LS.get('tour-'+PAG))setTimeout(balkje,1500);
}
window.rzTour={pagina:tourPagina,site:tourSite,welkom};
document.readyState==='loading'?addEventListener('DOMContentLoaded',init):init();
})();
