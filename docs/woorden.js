/* Woordenlijst-tooltips (5-10-2026). Vaktermen krijgen een stippellijn; aanwijzen, focussen of tikken toont een korte uitleg.
   Per blok (sectie, vlak, kaart, rij) alleen het eerste voorkomen van een term, zodat lange lijsten rustig blijven.
   Werkt ook voor inhoud die later wordt geladen (MutationObserver). Niet op de briefing (export moet schoon blijven) en niet in de Verkenner. */
(function(){
const PAG=(location.pathname.split('/').pop()||'').replace('.html','');
if(['briefing','verkenner','hulp'].includes(PAG))return;
const W=[
  [/\bmoties?\b/i,'Motie','Een verzoek van de raad aan het college, bijvoorbeeld om iets te onderzoeken of te regelen. De raad stemt erover: aangenomen of verworpen.'],
  [/\bamendement(en)?\b/i,'Amendement','Een voorstel om een raadsvoorstel te wijzigen. De raad stemt erover.'],
  [/\btoezegging(en)?\b/i,'Toezegging','Een belofte van een wethouder of de burgemeester aan de raad, bijvoorbeeld om informatie te sturen of iets uit te zoeken.'],
  [/\bafgedaan\b/i,'Afgedaan','Volgens de registratie van de griffie is de motie of toezegging uitgevoerd.'],
  [/\bover de termijn\b/i,'Over de termijn','De verwachte datum van afdoening is voorbij, maar het stuk staat nog niet als afgedaan geregistreerd.'],
  [/\braadsvoorstel(len)?\b/i,'Raadsvoorstel','Een voorstel van het college waarover de raad besluit, zoals een regel of een budget.'],
  [/\binitiatiefvoorstel(len)?\b/i,'Initiatiefvoorstel','Een voorstel dat een raadslid zelf indient.'],
  [/\bcollegebrie(f|ven)\b/i,'Collegebrief','Een brief van het college aan de raad, om te informeren of een toezegging af te doen.'],
  [/\bschriftelijke vragen\b/i,'Schriftelijke vragen','Vragen van een raadslid aan het college; het college antwoordt schriftelijk.'],
  [/\bwijkraad(advies|adviezen)\b/i,'Wijkraadadvies','Een advies van een wijkraad aan het college, gevraagd of ongevraagd.'],
  [/\bwijkra(a|de)den?\b/i,'Wijkraad','Gekozen bewoners die het college adviseren over hun wijk (sinds 2022).'],
  [/\bgemeenteblad\b/i,'Gemeenteblad','Waar de gemeente officieel bekendmaakt wat is vastgesteld: regels, vergunningen, verkeersbesluiten.'],
  [/\bcoalitieakkoord\b/i,'Coalitieakkoord','De afspraken van de partijen die samen het college vormen, voor 2026–2030.'],
  [/\bgriffie\b/i,'Griffie','De ambtelijke ondersteuning van de gemeenteraad. Houdt onder meer moties en toezeggingen bij.'],
  [/\bagendapunt(en)?\b/i,'Agendapunt','Een onderwerp op de agenda van een vergadering.'],
  [/\bbekendmaking(en)?\b/i,'Bekendmaking','Een officiële mededeling in het Gemeenteblad, zoals een vergunning of verkeersbesluit.'],
  [/\bverordening(en)?\b/i,'Verordening','Een regel die de gemeenteraad vaststelt en die voor iedereen in Rotterdam geldt.'],
];
const SKIP='a,button,input,textarea,select,label,option,h1,summary,header,nav,svg,script,style,code,.rz-term,.rzt-tip,.rzt-welkom,.rzt-menu,.rzt-balk,.rzw-tip,[contenteditable],.keuze,.zoekrij';
const BLOK='section,.vlak,.kblok,article,aside';
const css=`.rz-term{text-decoration:underline dotted #00811F 1.5px;text-underline-offset:3px;cursor:help;border-radius:2px}
.rz-term:hover,.rz-term:focus{background:#E1EFE2;outline:none}
.rzw-tip{position:fixed;z-index:9600;max-width:300px;background:#0F2A1A;color:#fff;border-radius:10px;padding:10px 13px;font:400 14px/1.45 var(--font,Arial);box-shadow:0 10px 28px rgba(0,0,0,.3)}
.rzw-tip b{display:block;margin-bottom:2px}.rzw-tip a{color:#9BE07A}`;
const st=document.createElement('style');st.textContent=css;document.head.appendChild(st);
let bezig=false,max=80,gedaan=0;
function verwerk(root){
  gedaan=root.querySelectorAll('.rz-term').length;if(gedaan>=max)return;bezig=true;
  const gezien=new WeakMap();   // blok -> set van termen
  const tw=document.createTreeWalker(root,NodeFilter.SHOW_TEXT,{acceptNode:n=>n.nodeValue.length>4&&n.parentElement&&!n.parentElement.closest(SKIP)?NodeFilter.FILTER_ACCEPT:NodeFilter.FILTER_REJECT});
  const nodes=[];while(tw.nextNode())nodes.push(tw.currentNode);
  for(const n of nodes){
    if(gedaan>=max)break;
    const blok=n.parentElement.closest(BLOK)||document.body;let set=gezien.get(blok);if(!set){set=new Set([...blok.querySelectorAll('.rz-term')].map(x=>x.dataset.t));gezien.set(blok,set);}
    for(const [rx,t,x] of W){
      if(set.has(t))continue;const m=rx.exec(n.nodeValue);if(!m)continue;
      const r=document.createRange();r.setStart(n,m.index);r.setEnd(n,m.index+m[0].length);
      const s=document.createElement('span');s.className='rz-term';s.tabIndex=0;s.dataset.t=t;s.dataset.x=x;s.setAttribute('role','button');s.setAttribute('aria-label',m[0]+': '+x);
      r.surroundContents(s);set.add(t);gedaan++;break;   // de rest van deze tekst komt bij een volgende ronde
    }
  }
  bezig=false;
}
/* tooltip */
let tip=null;
function toon(el){verberg();tip=document.createElement('div');tip.className='rzw-tip';tip.setAttribute('role','tooltip');
  tip.innerHTML=`<b>${el.dataset.t}</b>${el.dataset.x} <a href="hulp.html#woorden">Woordenlijst</a>`;document.body.appendChild(tip);
  const r=el.getBoundingClientRect(),w=tip.offsetWidth,h=tip.offsetHeight;let y=r.bottom+8;if(y+h>innerHeight-8)y=r.top-h-8;
  tip.style.left=Math.max(8,Math.min(r.left,innerWidth-w-8))+'px';tip.style.top=y+'px';}
function verberg(){if(tip){tip.remove();tip=null;}}
let hoverT;
document.addEventListener('mouseover',e=>{const t=e.target.closest&&e.target.closest('.rz-term');if(t){clearTimeout(hoverT);hoverT=setTimeout(()=>toon(t),250);}else if(!(e.target.closest&&e.target.closest('.rzw-tip'))){clearTimeout(hoverT);hoverT=setTimeout(verberg,200);}});
document.addEventListener('focusin',e=>{const t=e.target.closest&&e.target.closest('.rz-term');if(t)toon(t);});
document.addEventListener('focusout',e=>{if(e.target.closest&&e.target.closest('.rz-term'))setTimeout(verberg,150);});
document.addEventListener('click',e=>{const t=e.target.closest('.rz-term');if(t){e.preventDefault();e.stopPropagation();tip?verberg():toon(t);}else if(!e.target.closest('.rzw-tip'))verberg();},true);
addEventListener('scroll',verberg,{passive:true});
addEventListener('keydown',e=>{if(e.key==='Escape')verberg();});
/* eerste ronde + later geladen inhoud */
const main=document.querySelector('main')||document.body;
let t0;const plan=()=>{clearTimeout(t0);t0=setTimeout(()=>{for(let i=0;i<3;i++)verwerk(main);},350);};
new MutationObserver(()=>{if(!bezig)plan();}).observe(main,{childList:true,subtree:true});
plan();
})();
