/* Voorbeelddossier langs de keten gezegd -> besloten -> beloofd -> gedaan (eerst Parkeren).
   Gebruikt door dossier.html als er een d/<slug>-extra.json is. Eén subthemafilter bovenaan filtert alle lijsten;
   een inhoudsbalk loopt mee. Elke regel heeft dezelfde vorm (datum + status klein, titel groot) en een uitklap
   met het beloftespoor, de stemming of het videomoment. */
let KX=null,KD=null,KA=null,KSUB='',KWK=null,KKAART=null,KBEL='open',KAKK=null;
const kslug=s=>slug(s);
async function toonKeten(d,X,A){
  KD=d;KX=X;KA=A;CIT=[];verberg();KLAAG='n';KJR='alle';if(KSPEEL){clearInterval(KSPEEL);KSPEEL=null;}
  if(!KWK){try{[KWK,KKAART]=await Promise.all(['wijken.json','kaart.json'].map(f=>fetch(f).then(r=>r.json())));}catch(e){}}
  if(!KAKK){try{const r=await fetch('akkoord.json');if(r.ok)KAKK=await r.json();}catch(e){}}
  const h=decodeURIComponent(location.hash.slice(1)).split('/');KSUB=X.sub.find(s=>kslug(s)===h[1])||'';
  document.title=d.naam+' · raadzoeker';
  const crumb=(d.pad||[]).map(([t,u])=>`<a href="${u}">${esc(t)}</a>`).join(' › ')+' › '+esc(d.naam);
  const kinderen=ALLE.filter(x=>x.soort==='onderwerp'&&x.groep===d.naam),kr=d.soort==='domein'?ALLE.filter(x=>x.soort==='kruising'&&x.domein===d.slug):[];
  $('dossier').innerHTML=`<div class="crumb">${crumb}</div>
  <div class="kop"><h1>${esc(d.naam)}</h1>
    <div class="kopacties"><a class="knop" href="briefing.html#${d.slug}">Maak een briefing (A4, pdf of Word)</a><span class="sub" id="deelrij"></span>
      ${kinderen.length?`<span class="sub">Verdieping: ${kinderen.map(x=>`<a href="#${x.slug}">${esc(x.naam)}</a>`).join(' · ')}</span>`:''}
      ${kr.length?`<span class="sub">Per gebied: ${kr.map(x=>`<a href="#${x.slug}">${esc(x.gebied)}</a>`).join(' · ')}</span>`:''}
      ${(X.verwant||[]).length?`<span class="sub">Verwant: ${X.verwant.map(s=>ALLE.find(x=>x.slug===s)).filter(Boolean).map(x=>`<a href="#${x.slug}">${esc(x.naam)}</a>`).join(' · ')}</span>`:''}</div></div>
  <nav class="kbalk" aria-label="Onderdelen van dit dossier"><div class="kin">
    <div class="ksub" role="group" aria-label="Filter op subthema"><span class="sub">Filter:</span><button type="button" data-sub="">Alles</button>${X.sub.map(s=>`<button type="button" data-sub="${esc(s)}">${esc(s)}</button>`).join('')}</div>
    <div class="knav">${[['kort','Kort'],...(X.akkoord?[['akkoord','Akkoord']]:[]),['komt','Komt eraan'],['gezegd','Gezegd'],['besloten','Besloten'],['beloofd','Beloofd'],['gedaan','Gedaan'],['stad','In de stad'],['achtergrond','Achtergrond']].map(([i,t])=>`<a href="#${d.slug}" data-naar="${i}">${t}</a>`).join('')}</div></div></nav>
  <div id="kinh"></div>`;
  deel($('deelrij'),d.naam+' in de Rotterdamse raad',new URL('dossier.html?d='+d.slug,location.href).href);
  kTeken();window.scrollTo({top:0});
}
const kIn=x=>!KSUB||(x.sub||[]).includes(KSUB);
const kNu=(dt)=>dt&&dt<STAND;
function kSpoor(x){
  const st=x.stappen||[];if(!st.length)return '';
  return `<ol class="spoor">${st.map(s=>{const laat=s[1]==='verwacht'&&kNu(s[0]);
    const kl={ingediend:'z',stemming:'z',toegezegd:'z',tussenbericht:'m',commissieadvies:'m',afdoeningsvoorstel:'m',afgedaan:'k',verwacht:laat?'l':'o'}[s[1]]||'m';
    return `<li class="${kl}"><span class="dt">${fd(s[0])}</span><span>${s[3]?`<a href="${esc(s[3])}" target="_blank" rel="noopener">${esc(s[2])}</a>`:esc(s[2])}${laat?` <b>(${dagen(s[0],STAND)} dagen over de termijn)</b>`:''}</span></li>`;}).join('')}</ol>`;
}
function kStatus(x){
  const st=x.stappen||[],l=st[st.length-1];if(!l)return '';
  if(l[1]==='afgedaan')return `<span><span class="stip af"></span>Afgedaan ${fd(l[0])}</span>`;
  if(l[1]==='verwacht')return kNu(l[0])?`<span><span class="stip laat"></span>${dagen(l[0],STAND)} dagen over de termijn</span>`:`<span><span class="stip open"></span>Afdoening verwacht ${fd(l[0])}</span>`;
  return `<span><span class="stip open"></span>${esc(l[2])} ${fd(l[0])}</span>`;
}
function kRij(x){
  let ctx='';
  if(x.verzoek)ctx+=`<div><b>Verzoek aan het college</b> ‘${esc(x.verzoek)}’</div>`;
  if(x.toezegging)ctx+=`<div><b>Toegezegd</b> ‘${esc(x.toezegging)}’</div>`;
  if(x.stem)ctx+=stemHTML(x.stem);
  ctx+=`<div><b>Beloftespoor</b>${kSpoor(x)}</div><div><a href="${esc(x.url)}" target="_blank" rel="noopener">Open in iBabs</a></div>`;
  return `<details class="item"><summary><span class="meta"><span class="d">${fd(x.datum)}</span>${kStatus(x)}${x.wie?`<span class="wie">${esc(x.wie)}</span>`:''}</span><span class="t">${esc(x.titel)}</span><span class="pijl" aria-hidden="true">›</span></summary><div class="ctx">${ctx}</div></details>`;
}
function kDebat(x){
  const vid=x.video?`<button type="button" class="knop klein" data-video="${esc(x.video)}" data-sec="${x.sec}" data-titel="${esc(fd(x.datum)+' · '+(x.wie||x.verg))}">▶ Bekijk dit moment (${hms(Math.max(0,x.sec-3))})</button>`:'';
  return `<details class="item"><summary><span class="meta"><span class="d">${fd(x.datum)}</span><span>${esc(x.verg)}</span><span>${nf(x.n)}× genoemd</span><span class="wie">${esc(x.sprekers.slice(0,3).join(', '))}</span></span><span class="t">${esc(x.punt)}</span><span class="pijl" aria-hidden="true">›</span></summary>
    <div class="ctx"><div>‘${esc(x.fragment)}’<br><span class="sub">${esc(x.wie||'')}${x.partij?' ('+esc(x.partij)+')':''}${x.auto?' · automatische ondertiteling, kan fouten bevatten':''}</span></div>
    <div style="display:flex;gap:12px;flex-wrap:wrap;align-items:center">${vid}<a href="https://gemeenteraad.rotterdam.nl/Agenda/Index/${esc(x.agenda)}" target="_blank" rel="noopener">Vergadering in iBabs</a></div></div></details>`;
}
const hms=s=>{s=Math.round(s);const h=Math.floor(s/3600),m=Math.floor(s%3600/60),z=s%60;return (h?h+':':'')+String(m).padStart(h?2:1,'0')+':'+String(z).padStart(2,'0');};
function kSectie(id,titel,stap,intro,inh){return `<section class="vlak ksec" id="k-${id}" aria-labelledby="k-${id}h">${stap?`<div class="kstap">${stap}</div>`:''}<h2 id="k-${id}h">${titel}</h2>${intro?`<p class="intro">${intro}</p>`:''}${inh}</section>`;}
function kMeer(id,items,n,fn,leeg){
  if(!items.length)return `<p class="leeg">${leeg}</p>`;
  return `<div class="lijst">${items.slice(0,n).map(fn).join('')}</div>${items.length>n?`<button type="button" class="meerknop" aria-expanded="false" aria-controls="${id}"><span class="tx">Toon alle ${items.length}</span><span class="pijl" aria-hidden="true">▾</span></button><div class="inh lijst" id="${id}" hidden>${items.slice(n).map(fn).join('')}</div>`:''}`;
}
function kTeken(){
  const d=KD,X=KX,A=KA,sub=KSUB;
  document.querySelectorAll('.ksub button').forEach(b=>b.setAttribute('aria-pressed',b.dataset.sub===sub));
  const mot=X.spoor.filter(x=>x.soort==='motie'&&kIn(x)),toez=X.spoor.filter(x=>x.soort==='toezegging'&&kIn(x));
  const deb=X.debatten.filter(kIn),vast=X.vastgesteld.filter(kIn),komt=X.komt.filter(kIn),vs=X.voorstellen.filter(kIn);
  const gedaan=[...mot,...toez].filter(x=>!x.open).sort((a,b)=>{const la=a.stappen[a.stappen.length-1][0],lb=b.stappen[b.stappen.length-1][0];return lb.localeCompare(la);});
  const open=[...mot,...toez].filter(x=>x.open),laat=open.filter(x=>{const l=x.stappen[x.stappen.length-1];return l[1]==='verwacht'&&kNu(l[0]);});
  const fl=sub?` <span class="sub">· gefilterd op ${esc(sub.toLowerCase())}</span>`:'';
  CIT=[];
  let h='';
  // 1 kort: verhaal en stand
  const k=A&&A.kern||[];
  h+=`<section class="vlak ksec" id="k-kort" aria-labelledby="k-korth"><div class="kkort"><div><h2 id="k-korth">In het kort <span class="ai">AI-samenvatting</span></h2>
      <p class="kern">${k.length?alinea(k.slice(0,-1)):d.tsum?esc(d.tsum.kern):'<span class="sub">De AI-samenvatting van dit dossier wordt nog gemaakt. Hieronder staat alles wat de raad zei, besloot en beloofde.</span>'}</p><p class="sub" style="font-size:13px;margin-top:8px">Wijs een zin aan of tik erop voor het letterlijke citaat en de bron.</p></div>
    <div>${k.length?`<section class="stand"><div class="t">Stand van zaken · AI</div><p>${zin(k[k.length-1])}</p></section>`:''}
      <div class="cijfers" style="margin-top:12px"><div class="cijfer"><span class="groot num">${nf(open.length)}</span>beloftes open<div class="sub">${laat.length?`<span class="stip laat"></span>${laat.length} over de termijn`:'geen over de termijn'}</div></div>
      <div class="cijfer"><span class="groot num">${nf(komt.length+vs.length)}</span>komt eraan<div class="sub">deadlines en voorstellen</div></div></div></div></div>
    <ol class="keten" aria-label="De keten">${[['gezegd','Gezegd',`${deb.length} debatten`],['besloten','Besloten',`${mot.length} moties · ${vast.length} regels`],['beloofd','Beloofd',`${toez.length} toezeggingen`],['gedaan','Gedaan',`${gedaan.length} afgedaan`]].map(([i,t,n])=>`<li><a href="#${d.slug}" data-naar="${i}"><b>${t}</b><span>${n}</span></a></li>`).join('')}</ol></section>`;
  // 1b coalitieakkoord: wat het nieuwe college van plan is (letterlijke passages + punten uit de samenvatting van het akkoord)
  const AK=X.akkoord;
  if(AK&&AK.passages.length){const dp=KAKK&&KAKK.domeinen&&KAKK.domeinen[AK.domein]||[];
    h+=kSectie('akkoord','Coalitieakkoord 2026–2030','',`Het akkoord ‘Vaart maken’ van PRO, D66, VVD, CDA en Volt (juli 2026) zet de toon voor de komende jaren. Dit staat erin over ${esc(d.naam.toLowerCase())}, letterlijk overgenomen. <a href="akkoord.html">Samenvatting van het hele akkoord</a> · <a href="${esc(AK.url)}" target="_blank" rel="noopener">Het akkoord (pdf)</a>`,
      `<div class="kakk">${AK.passages.map(([t,b])=>`<blockquote><p>‘${esc(t)}’</p><a class="sub" href="${esc(AK.url)}#page=${b}" target="_blank" rel="noopener">blz. ${b}</a></blockquote>`).join('')}</div>`+
      (dp.length?blok('kak','Het akkoord over dit domein',`<p class="intro">Uit de samenvatting van het akkoord, bij het domein ${esc((ALLE.find(x=>x.soort==='domein'&&x.slug.startsWith(AK.domein))||{naam:AK.domein}).naam.toLowerCase())}.</p>`,dp.map(x=>`<div class="pt">${rijAI(x)}</div>`).join(''),`Toon ${dp.length} punten`,true).replace('class="vlak deel"','class="deel binnen"'):''));}
  // 2 komt eraan
  h+=kSectie('komt','Komt eraan'+fl,'','Raadsvoorstellen die nog behandeld worden en beloftes met een deadline na '+fd(STAND)+'.',
    (vs.length?`<div class="lijst">${vs.map(v=>`<details class="item"><summary><span class="meta"><span class="d">${fd(v.datum)}</span><span><span class="stip open"></span>Raadsvoorstel${v.behandeling?' · '+esc(v.behandeling.slice(0,80)):''}</span></span><span class="t">${esc(v.titel)}</span><span class="pijl" aria-hidden="true">›</span></summary><div class="ctx"><div><a href="${esc(v.url)}" target="_blank" rel="noopener">Open in iBabs</a></div></div></details>`).join('')}</div>`:'')+
    kMeer('kk',komt,5,kRij,'Geen deadlines in de komende tijd.'));
  // 3 gezegd
  const F=A&&A.fracties;
  h+=kSectie('gezegd','Gezegd'+fl,'1 · gezegd',`Debatten in de raad en de commissies sinds 2022 waarin het meest over ${esc(d.naam.toLowerCase())} werd gesproken, nieuwste eerst. Klap open voor het fragment en het videomoment.`,
    kMeer('kg',deb,6,kDebat,'Geen debatten bij dit subthema.')+
    (F&&F.punten&&F.punten.length?blok('kf','Wat de fracties vinden',`<p class="intro">${alinea(F.intro||[])}</p>`,F.punten.map(f=>`<div class="pt"><b>${esc(f.fractie)}</b> ${f.standpunten.map(x=>`${esc(x.wat.replace(/\.$/,''))} ${bron(x)}${cl(x)}`).join('; ')}</div>`).join(''),`Toon ${F.punten.length} fracties`,true).replace('class="vlak deel"','class="deel binnen"'):''));
  // 4 besloten
  const S=X.stemmen;
  h+=kSectie('besloten','Besloten'+fl,'2 · besloten','Aangenomen moties (met het verzoek aan het college en de stemming) en de regels die daarna zijn vastgesteld in het Gemeenteblad.',
    `<div class="ktwee"><div><h3>Aangenomen moties</h3>${kMeer('km',mot,6,kRij,'Geen aangenomen moties bij dit subthema.')}</div>
     <div><h3>Vastgesteld</h3>${vast.length?`<div class="lijst">${vast.slice(0,8).map(v=>`<div class="pt kvast"><span class="sub">${fd(v.datum)} · ${esc(v.soort)}${v.n>1?` · ${v.n} versies`:''}</span><br><a href="${esc(v.url)}" target="_blank" rel="noopener">${esc(v.titel)}</a></div>`).join('')}</div>`:'<p class="leeg">Niets gevonden.</p>'}</div></div>
     ${S.fracties.length?`<h3 style="margin-top:24px">Hoe stemden de fracties?</h3><p class="sub" style="margin:4px 0 12px">Bij ${S.n} moties over ${esc(d.naam.toLowerCase())} sinds 2022 met een hoofdelijke stemming (alle subthema's). Op alfabet; alleen fracties met minstens 5 stemmingen.</p>
       <div class="kstem">${[...S.fracties].sort((a,b)=>a[0].localeCompare(b[0])).map(([p,v,t])=>`<div><span>${esc(p)}</span><span class="bar" role="img" aria-label="${v} voor, ${t} tegen"><i style="width:${v/(v+t)*100}%"></i></span><span class="sub num">${v} voor · ${t} tegen</span></div>`).join('')}</div>`:''}`);
  // 5 beloofd
  const C=A&&A.college;
  const bl={open:open,laat:laat,af:gedaan}[KBEL]||open;
  h+=kSectie('beloofd','Beloofd'+fl,'3 · beloofd','Toezeggingen van het college en aangenomen moties die nog uitgevoerd moeten worden. Klap open voor het beloftespoor: wanneer het college iets liet weten en wat er nog moet komen.',
    `<div class="chips filters">${[['open','Open',open.length],['laat','Over de termijn',laat.length],['af','Afgedaan',gedaan.length]].map(([k,t,n])=>`<button type="button" data-bel="${k}" aria-pressed="${k===KBEL}" class="${k===KBEL?'on':''}">${t} (${n})</button>`).join('')}</div>`+
    kMeer('kb',bl,8,kRij,'Niets in deze lijst.')+
    (C&&C.punten&&C.punten.length?blok('kc','Wat het college beloofde en deed',`<p class="intro">${alinea(C.intro||[])}</p>`,C.punten.map(x=>`<div class="pt">${rijAI(x)}</div>`).join(''),`Toon ${C.punten.length} punten`,true).replace('class="vlak deel"','class="deel binnen"'):''));
  // 6 gedaan
  const dl=gedaan.map(x=>dagen(x.datum,x.stappen[x.stappen.length-1][0])).filter(v=>v>=0).sort((a,b)=>a-b),med=dl.length?dl[Math.floor(dl.length/2)]:null;
  h+=kSectie('gedaan','Gedaan'+fl,'4 · gedaan',`Moties en toezeggingen die zijn afgedaan, nieuwste eerst.${med!==null?` Van belofte tot afdoening duurde het meestal (mediaan) <b>${med} dagen</b>.`:''}`,
    kMeer('kd',gedaan,6,kRij,'Nog niets afgedaan bij dit subthema.'));
  // 7 in de stad
  const W=A&&A.wijken;
  h+=kSectie('stad','In de stad','','Waar in Rotterdam het over '+esc(d.naam.toLowerCase())+' gaat: wijkraadstukken, verkeersbesluiten en raadsstukken die de wijk noemen (alle subthema\'s). Klik op een wijk.',
    ((X.lagen||[]).length?`<div class="klagen" role="group" aria-label="Kaartlaag">${X.lagen.map(([id,t])=>`<button type="button" data-laag="${id}" aria-pressed="${id===KLAAG}">${esc(t)}</button>`).join('')}</div>
      <div class="kjaar" id="kjaar" ${KLAAG==='vg'?'':'hidden'}><label for="kjr">Jaar</label><input type="range" id="kjr" min="2018" max="2026" step="1" value="${KJR}"><b id="kjrv">${KJR==='alle'?'alle jaren':KJR}</b><button type="button" class="knop wit klein" id="kspeel">▶ Afspelen</button><button type="button" class="wis" id="kalle">alle jaren</button></div>`:'')+
    `<div class="kstad"><div class="kkaart" id="kkaart"></div><div id="kwijk"><p class="sub">Klik op een wijk${(X.projecten||[]).length?' of een project (●)':''} op de kaart.</p></div></div>`+
    ((X.projecten||[]).length?`<h3 style="margin-top:20px">Grote projecten</h3><p class="sub" style="margin:0 0 8px">Waar de raad het over had, op de plek die de stukken het vaakst noemen. Klik voor de nieuwste stukken.</p><div class="kproj">${X.projecten.map((p,i)=>{const J=['2018','2019','2020','2021','2022','2023','2024','2025','2026'],m=Math.max(1,...J.map(j=>p.per[j]||0));
      return `<button type="button" class="kp" data-proj="${i}"><b>${esc(p.naam)}</b><span class="sub">${esc(p.wijknaam)} · ${nf(p.n)} stukken</span><span class="kspark" aria-hidden="true">${J.map(j=>`<i style="height:${Math.max(2,(p.per[j]||0)/m*22)}px" title="${j}: ${p.per[j]||0}"></i>`).join('')}</span></button>`;}).join('')}</div>`:'')+
    (W&&W.punten&&W.punten.length?blok('kw','Signalen uit de wijken',`<p class="intro">${alinea(W.intro||[])}</p>`,W.punten.map(x=>`<div class="pt"><b>${esc(x.wijk)}</b> ${rijAI(x)}</div>`).join(''),`Toon ${W.punten.length} signalen`,true).replace('class="vlak deel"','class="deel binnen"'):''));
  // 8 achtergrond
  const T=A&&A.tijdlijn,O=A&&A.open;
  let ach='';
  if(A&&A.verdieping&&A.verdieping.length)ach+=blok('kv','Meer diepgang',`<p class="intro">${alinea(A.verdieping[0])}</p>`,A.verdieping.length>1?`<div class="verd">${A.verdieping.slice(1).map(a=>`<p>${alinea(a)}</p>`).join('')}</div>`:'','Lees verder',true).replace('class="vlak deel"','class="deel binnen"');
  if(T&&T.punten&&T.punten.length)ach+=blok('kt','Tijdlijn',`<p class="intro">${alinea(T.intro||[])}</p>`,`<div class="tlr">${T.punten.map(x=>`<div class="d">${fd(x.bron_datum)}</div><div class="pt">${rijAI(x)}</div>`).join('')}</div><div style="margin-top:16px">${tijdlijnSvg(d)}</div>`,`Toon ${T.punten.length} momenten en de grafiek`,true).replace('class="vlak deel"','class="deel binnen"');
  if(O&&O.punten&&O.punten.length)ach+=blok('ko','Open eindjes',`<p class="intro">${alinea(O.intro||[])}</p>`,O.punten.map(x=>`<div class="pt">${rijAI(x)}</div>`).join(''),`Toon ${O.punten.length} punten`,true).replace('class="vlak deel"','class="deel binnen"');
  ach+=blok('kcij','Cijfers',`<p class="intro">Aandacht per jaar en wie erover praat.</p>`,`<div class="cijferblok" style="margin-top:16px"><section class="grafiek"><h3>Aandacht per jaar</h3>${trendSvg(d)}<p class="sub">${d.eenheid==='procent'?'Aandeel van alle gesproken woorden in de raad, in procenten.':'Keren genoemd per 100.000 gesproken woorden in de raad.'}</p></section><section><h3>Wie praat erover?</h3><div class="balken">${d.partijen.slice(0,8).map(p=>`<div class="balk2"><span>${esc(p[0])}</span><i style="width:${p[1]/Math.max(...d.partijen.map(q=>q[1]))*100}%"></i><span class="v num">${String(p[1]).replace('.',',')}</span></div>`).join('')}</div><p class="sub" style="margin-top:8px">${d.eenheid==='procent'?'Aandeel van de spreektijd van die fractie, in procenten.':'Per 100.000 woorden van die fractie.'} Geen oordeel; alleen hoe vaak het onderwerp terugkomt.</p></section></div>`,'Toon cijfers').replace('class="vlak deel"','class="deel binnen"');
  h+=kSectie('achtergrond','Achtergrond','','Het hele verhaal: meer diepgang, het verloop in de tijd, wat nog open is en de cijfers.',ach);
  $('kinh').innerHTML=h;
  kKaart();kVolg();
}
let KLAAG='n',KJR='alle',KSPEEL=null;
function kWaarde(w){
  if(KLAAG==='n')return Object.values(w.n||{}).reduce((a,b)=>a+b,0);
  if(KLAAG==='vg')return KJR==='alle'?Object.values(w.vg||{}).reduce((a,b)=>a+b,0):((w.vg||{})[KJR]||0);
  return w[KLAAG];
}
function kKaart(){
  if(!KWK||!KKAART||!$('kkaart'))return;
  const per=Object.fromEntries(KX.wijken.map(w=>[w.slug,w])),vals=KX.wijken.map(kWaarde).filter(v=>v!=null),mx=Math.max(1,...vals),mn=['huur','corp','woz'].includes(KLAAG)?Math.min(...vals):0;
  const f=v=>v==null?null:(v-mn)/Math.max(1e-9,mx-mn),kl=x=>x==null?'#EFF4F6':x>.8?'#004C31':x>.6?'#00811F':x>.4?'#4EB051':x>.2?'#99CCA0':'#E1EFE2';
  const laag=(KX.lagen||[]).find(l=>l[0]===KLAAG);
  const proj=(KX.projecten||[]).map((p,i)=>`<g class="kpm" data-proj="${i}" tabindex="0" role="button" aria-label="${esc(p.naam)}"><circle cx="${p.lx}" cy="${p.ly}" r="${(4+Math.sqrt(p.n)/2).toFixed(1)}" fill="#00548F" fill-opacity=".85" stroke="#fff" stroke-width="1.5"/><title>${esc(p.naam)}: ${p.n} stukken</title></g>`).join('');
  $('kkaart').innerHTML=`<svg viewBox="0 0 ${KKAART.w} ${KKAART.h}" role="img" aria-label="Kaart van Rotterdam per wijk"><path class="h" d="${KKAART.havens}"/>${KWK.wijken.map(w=>{const x=per[w.slug],v=x?kWaarde(x):null;
    return `<path class="wk" data-w="${w.slug}" d="${w.d}" tabindex="0" fill="${kl(f(v))}"><title>${esc(w.naam)}: ${v==null?'geen gegevens':nf(Math.round(v*10)/10)}</title></path>`;}).join('')}<path class="w" d="${KKAART.water}"/>${proj}</svg>
    <p class="sub" style="margin-top:6px">${laag?esc(laag[1])+': '+esc(laag[2])+'. ':''}Donkerder = meer${['huur','corp','woz'].includes(KLAAG)?'; cijfers ter vergelijking, geen oordeel':'. Aantallen zijn een indicatie: ‘genoemd in’ klopt in ongeveer 9 van de 10 gevallen'}.</p>`;
}
function kWijk(s){
  const x=KX.wijken.find(w=>w.slug===s);if(!x)return;
  document.querySelectorAll('#kkaart path.wk').forEach(p=>p.classList.toggle('sel',p.dataset.w===s));
  const t={raad:'raadsstukken en debatten die de wijk noemen',wijkraad:'stukken van de wijkraad',verkeersbesluit:'verkeersbesluiten',besluit:'andere besluiten'};
  const vg=x.vg?Object.values(x.vg).reduce((a,b)=>a+b,0):null;
  $('kwijk').innerHTML=`<h3>${esc(x.naam)} <span class="sub">· ${esc(x.gebied)}</span></h3>
    <ul class="kn">${Object.entries(t).filter(([k])=>(x.n||{})[k]).map(([k,l])=>`<li><b class="num">${nf(x.n[k])}</b> ${l}</li>`).join('')}${vg!=null?`<li><b class="num">${nf(vg)}</b> omgevingsvergunningen sinds 2018</li>`:''}</ul>
    ${x.huur!=null?`<p class="sub" style="margin:8px 0 0">Ter vergelijking (CBS 2024): ${x.huur}% huurwoningen, ${x.corp}% van corporaties, WOZ € ${nf(Math.round(x.woz))}.000.</p>`:''}
    ${x.recent.length?`<p class="sub" style="margin:8px 0 4px">Laatste besluiten over ${esc(KD.naam.toLowerCase())}:</p>${x.recent.map(r=>`<div class="pt" style="font-size:14px;padding:6px 0"><span class="sub">${fd(r[0])}</span><br><a href="${esc(r[2])}" target="_blank" rel="noopener">${esc(r[1])}</a></div>`).join('')}`:''}
    <p style="margin-top:8px"><a href="wijk.html#w-${x.slug}">Naar de wijk ${esc(x.naam)}</a> · <a href="zoek.html#q=${encodeURIComponent(x.naam)}&d=${encodeURIComponent(KD.domein||'')}">Zoek in de stukken</a></p>`;
}
function kProj(i){
  const p=KX.projecten[i];if(!p)return;
  document.querySelectorAll('.kp').forEach(b=>b.classList.toggle('on',b.dataset.proj===String(i)));
  $('kwijk').innerHTML=`<h3>${esc(p.naam)} <span class="sub">· ${esc(p.wijknaam)}</span></h3><p class="sub">${nf(p.n)} stukken sinds 2018 die het project noemen. De nieuwste:</p>
    ${p.recent.map(r=>`<div class="pt" style="font-size:14px;padding:6px 0"><span class="sub">${fd(r[0])} · ${esc(r[1])}</span><br><a href="${esc(r[3])}" target="_blank" rel="noopener">${esc(r[2])}</a></div>`).join('')}
    <p style="margin-top:8px"><a href="zoek.html#q=${encodeURIComponent('"'+p.zoek.toLowerCase()+'"')}&vanaf=alle">Alle stukken over ${esc(p.zoek)}</a></p>`;
  const k=$('kwijk');if(k.getBoundingClientRect().top<0||k.getBoundingClientRect().top>innerHeight)k.scrollIntoView({behavior:'smooth',block:'center'});
}
/* inhoudsbalk: markeer het onderdeel dat in beeld is */
let KOBS=null;
function kVolg(){
  if(KOBS)KOBS.disconnect();
  KOBS=new IntersectionObserver(es=>{es.forEach(e=>{if(e.isIntersecting){const id=e.target.id.slice(2);document.querySelectorAll('.knav a').forEach(a=>a.classList.toggle('on',a.dataset.naar===id));}});},{rootMargin:'-120px 0px -60% 0px'});
  document.querySelectorAll('.ksec').forEach(s=>KOBS.observe(s));
}
document.addEventListener('click',e=>{
  if(!KX||!document.querySelector('.kbalk'))return;
  const n=e.target.closest('[data-naar]');if(n){e.preventDefault();const s=$('k-'+n.dataset.naar);if(s)window.scrollTo({top:s.getBoundingClientRect().top+scrollY-(document.querySelector('.kbalk').offsetHeight+12),behavior:'smooth'});return;}
  const b=e.target.closest('[data-sub]');if(b){KSUB=b.dataset.sub;history.replaceState(null,'','#'+KD.slug+(KSUB?'/'+kslug(KSUB):''));const y=scrollY;kTeken();window.scrollTo({top:y});return;}
  const bl=e.target.closest('[data-bel]');if(bl){KBEL=bl.dataset.bel;const y=scrollY;kTeken();window.scrollTo({top:y});return;}
  const w=e.target.closest('#kkaart path.wk');if(w){kWijk(w.dataset.w);return;}
  const pj=e.target.closest('[data-proj]');if(pj){kProj(+pj.dataset.proj);return;}
  const lg=e.target.closest('[data-laag]');if(lg){KLAAG=lg.dataset.laag;document.querySelectorAll('[data-laag]').forEach(b=>b.setAttribute('aria-pressed',b===lg));$('kjaar').hidden=KLAAG!=='vg';kKaart();return;}
  if(e.target.id==='kalle'){KJR='alle';$('kjrv').textContent='alle jaren';kKaart();return;}
  if(e.target.id==='kspeel'){if(KSPEEL){clearInterval(KSPEEL);KSPEEL=null;e.target.textContent='▶ Afspelen';return;}
    let j=2018;e.target.textContent='❚❚ Stop';const stap=()=>{KJR=String(j);$('kjr').value=j;$('kjrv').textContent=j;kKaart();j++;if(j>2026){clearInterval(KSPEEL);KSPEEL=null;e.target.textContent='▶ Afspelen';}};stap();KSPEEL=setInterval(stap,900);return;}
  const v=e.target.closest('[data-video]');if(v){kVideo(v.dataset.video,+v.dataset.sec,v.dataset.titel);}
});
document.addEventListener('input',e=>{if(e.target.id==='kjr'){KJR=e.target.value;$('kjrv').textContent=KJR;kKaart();}});
document.addEventListener('keydown',e=>{const p=e.target.closest&&e.target.closest('[data-proj]');if(p&&p.tagName!=='BUTTON'&&(e.key==='Enter'||e.key===' ')){e.preventDefault();kProj(+p.dataset.proj);}});
document.addEventListener('keydown',e=>{const w=e.target.closest&&e.target.closest('#kkaart path.wk');if(w&&(e.key==='Enter'||e.key===' ')){e.preventDefault();kWijk(w.dataset.w);}});
/* videospeler: springt naar het moment (zelfde aanpak als het archief) */
function kVideo(ref,sec,titel){
  sec=Math.max(0,sec-3);let m=$('kvid');
  if(!m){m=document.createElement('div');m.id='kvid';m.innerHTML=`<div class="kvb" role="dialog" aria-modal="true" aria-labelledby="kvt"><div class="kvk"><b id="kvt"></b><button type="button" class="knop wit klein" id="kvj"></button><button type="button" class="knop wit klein" id="kvx" aria-label="Sluiten">Sluiten</button></div><div id="kvbox" class="kvbox"></div><p class="sub" id="kvn"></p></div>`;document.body.appendChild(m);
    m.addEventListener('click',e=>{if(e.target===m||e.target.id==='kvx')kSluit();});}
  m.hidden=false;$('kvt').textContent=titel;$('kvj').textContent='Spring naar '+hms(sec);
  $('kvn').textContent='Klik in de speler op Start; de uitzending begint dan op '+hms(sec)+'. Staat hij ergens anders, klik dan op ‘Spring naar’. De tijd is bij benadering.';
  const box=$('kvbox');box.innerHTML='';let jump=()=>{};
  if(ref.startsWith('c:')){const go=()=>{try{const p=cwc.sdk.player.client.createPlayer({id:ref.slice(2),display:126});p.element.style.cssText='width:100%;height:100%;border:0';p.element.setAttribute('allow','fullscreen; autoplay');box.appendChild(p.element);
      jump=()=>{try{p.seek({timestamp:sec*1000});}catch(e){}};m._stop=()=>{try{p.destroy();}catch(e){}};try{p.on('ready',jump);}catch(e){}setTimeout(jump,2500);setTimeout(jump,6000);}catch(e){box.textContent='De speler kon niet worden geladen.';}};
    if(window.cwc&&cwc.sdk)go();else{const sc=document.createElement('script');sc.src='https://sdk.companywebcast.com/sdk/player/client.js';sc.onload=go;sc.onerror=()=>{box.textContent='De speler kon niet worden geladen.';};document.head.appendChild(sc);}}
  else{const f=document.createElement('iframe');f.allow='fullscreen; autoplay';f.style.cssText='width:100%;height:100%;border:0';f.src='https://connectlive.ibabs.eu/Player/Player/'+ref.slice(2);box.appendChild(f);
    jump=()=>{try{f.contentWindow.postMessage({action:'jumpToPosition',seconds:sec},'https://connectlive.ibabs.eu/');}catch(e){}};f.onload=()=>{setTimeout(jump,2500);setTimeout(jump,6000);};}
  $('kvj').onclick=()=>jump();
}
function kSluit(){const m=$('kvid');if(!m)return;if(m._stop)m._stop();m._stop=null;$('kvbox').innerHTML='';m.hidden=true;}
document.addEventListener('keydown',e=>{if(e.key==='Escape')kSluit();});
