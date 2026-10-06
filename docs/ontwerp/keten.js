/* Voorbeelddossier langs de keten gezegd -> besloten -> beloofd -> gedaan (indeling 1, 5-10-2026: overzicht met uitklapblokken).
   Gebruikt door dossier.html als er een d/<slug>-extra.json is. De pagina begint kort: de kern, wat eraan komt, en per stap
   één blok met een samenvattende regel en de 3 nieuwste punten. 'Toon alles' klapt een blok open; pas dan verschijnt het filter
   op subthema, direct boven de lijst die het filtert. Een open blok staat in de link (#parkeren/besloten). */
let KX=null,KD=null,KA=null,KWK=null,KKAART=null,KBEL='open',KAKK=null,KPK=null;
let KOPEN=new Set(),KSUB={};
const kslug=s=>slug(s);
async function toonKeten(d,X,A){
  KD=d;KX=X;KA=A;CIT=[];verberg();KLAAG='n';KJR='alle';PJR='2026';if(KSPEEL){clearInterval(KSPEEL);KSPEEL=null;}KSUB={};KBEL='open';
  if(!KWK){try{[KWK,KKAART]=await Promise.all(['wijken.json','kaart.json'].map(f=>fetch(f).then(r=>r.json())));}catch(e){}}
  if(!KAKK){try{const r=await fetch('akkoord.json');if(r.ok)KAKK=await r.json();}catch(e){}}
  KPK=null;try{const r=await fetch('d/'+d.slug+'-kaart.json');if(r.ok)KPK=await r.json();}catch(e){}
  const h=decodeURIComponent(location.hash.slice(1)).split('/');KOPEN=new Set(h[1]?[h[1]]:[]);
  document.title=d.naam+' · raadzoeker';
  const crumb=(d.pad||[]).map(([t,u])=>`<a href="${u}">${esc(t)}</a>`).join(' › ')+' › '+esc(d.naam);
  const kinderen=ALLE.filter(x=>x.soort==='onderwerp'&&x.groep===d.naam),kr=d.soort==='domein'?ALLE.filter(x=>x.soort==='kruising'&&x.domein===d.slug):[];
  const verw=(X.verwant||[]).map(s=>ALLE.find(x=>x.slug===s)).filter(Boolean);
  $('dossier').innerHTML=`<div class="crumb">${crumb}</div>
  <div class="kop"><h1>${esc(d.naam)}</h1>
    <div class="kopacties">${volgKnop(d.slug,d.naam)}<a class="knop" href="briefing.html#${d.slug}">Briefing<span class="lang"> maken (A4, pdf of Word)</span></a><span class="sub" id="deelrij"></span></div>
    ${kinderen.length||kr.length||verw.length?`<div class="kverw">${kinderen.length?`<span><b>Onderwerpen:</b> ${kinderen.map(x=>`<a href="#${x.slug}">${esc(x.naam)}</a>`).join(' · ')}</span>`:''}
      ${verw.length?`<span><b>Verwant:</b> ${verw.map(x=>`<a href="#${x.slug}">${esc(x.naam)}</a>`).join(' · ')}</span>`:''}
      ${kr.length?`<span><b>Per gebied:</b> ${kr.map(x=>`<a href="#${x.slug}">${esc(x.gebied)}</a>`).join(' · ')}</span>`:''}</div>`:''}</div>
  <div id="kinh"></div>`;
  deel($('deelrij'),d.naam+' in de Rotterdamse raad',new URL('dossier.html?d='+d.slug,location.href).href);
  kTeken();
  if(KOPEN.size){const s=$('k-'+[...KOPEN][0]);if(s)setTimeout(()=>s.scrollIntoView({block:'start'}),50);}else window.scrollTo({top:0});
}
const kIn=(id,x)=>!KSUB[id]||(x.sub||[]).includes(KSUB[id]);
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
/* ---------- de blokken ---------- */
function kLijsten(){
  const X=KX,mot=X.spoor.filter(x=>x.soort==='motie'),toez=X.spoor.filter(x=>x.soort==='toezegging');
  const af=[...mot,...toez].filter(x=>!x.open).sort((a,b)=>b.stappen[b.stappen.length-1][0].localeCompare(a.stappen[a.stappen.length-1][0]));
  const open=[...mot,...toez].filter(x=>x.open),laat=open.filter(x=>{const l=x.stappen[x.stappen.length-1];return l[1]==='verwacht'&&kNu(l[0]);});
  open.sort((a,b)=>(laat.includes(b)-laat.includes(a))||b.datum.localeCompare(a.datum));
  return {mot,toez,af,open,laat};
}
/* filter op subthema: alleen subthema's die in deze lijst voorkomen, met aantallen; staat direct boven de lijst */
function kFilter(id,items){
  const n={};items.forEach(x=>(x.sub||[]).forEach(s=>n[s]=(n[s]||0)+1));
  const subs=KX.sub.filter(s=>n[s]);if(subs.length<2)return '';
  return `<div class="kfilter" role="group" aria-label="Toon over"><span class="sub">Toon over:</span><button type="button" data-ksub="${id}|" aria-pressed="${!KSUB[id]}">Alles (${items.length})</button>${subs.map(s=>`<button type="button" data-ksub="${id}|${esc(s)}" aria-pressed="${KSUB[id]===s}">${esc(s)} (${n[s]})</button>`).join('')}</div>`;
}
function kBlok(id,stap,titel,telling,regel,inhoud,{kleur='',open=KOPEN.has(id)}={}){
  return `<section class="kblok ${kleur}${open?' open':''}" id="k-${id}"><button type="button" class="kkop" data-blok="${id}" aria-expanded="${open}" aria-controls="k-${id}i">
    <span class="kt">${stap?`<span class="kstap">${stap}</span>`:''}${titel}</span><span class="kn">${telling}</span><span class="kpijl" aria-hidden="true">▾</span>${regel?`<span class="kr">${regel}</span>`:''}</button>
    <div class="kbody" id="k-${id}i">${inhoud(open)}</div></section>`;
}
/* lijst: dicht de eerste 3, open alles met filter erboven */
function kLijst(id,items,fn,leeg,open,n=3){
  const f=items.filter(x=>kIn(id,x));
  if(!open)return items.length?`<div class="lijst">${items.slice(0,n).map(fn).join('')}</div>${items.length>n?`<button type="button" class="kmeer" data-blok="${id}">Toon alle ${nf(items.length)}</button>`:''}`:`<p class="leeg">${leeg}</p>`;
  return kFilter(id,items)+(f.length?`<div class="lijst">${f.map(fn).join('')}</div>`:`<p class="leeg">${leeg}</p>`);
}
const kBinnen=h=>h.replace('class="vlak deel"','class="deel binnen"');
function kTeken(){
  const d=KD,X=KX,A=KA,L=kLijsten();CIT=[];
  const k=A&&A.kern||[];
  let h=`<section class="vlak kkort2"><div><h2>In het kort ${k.length?'<span class="ai">AI-samenvatting</span>':d.tsum?'<span class="ai">korte AI-samenvatting</span>':''}</h2>
      <p class="kern">${k.length?alinea(k.slice(0,-1)):d.tsum?esc(d.tsum.kern):'<span class="sub">De samenvatting van dit dossier wordt nog gemaakt.</span>'}</p>
      ${A&&A.verdieping?`<p style="margin-top:8px"><a href="#${d.slug}/achtergrond" data-openen="achtergrond">Lees het hele verhaal</a> <span class="sub">· wijs een zin aan voor het citaat en de bron</span></p>`:''}</div>
    <div>${k.length?`<section class="stand"><div class="t">Stand van zaken · AI</div><p>${zin(k[k.length-1])}</p></section>`:''}
      <div class="cijfers" style="margin-top:12px"><div class="cijfer"><span class="groot num">${nf(L.open.length)}</span>beloftes open<div class="sub">${L.laat.length?`<span class="stip laat"></span>${L.laat.length} over de termijn`:'geen over de termijn'}</div></div>
      <div class="cijfer"><span class="groot num">${nf(X.debatten.length)}</span>debatten<div class="sub">sinds 2022</div></div></div></div></section>`;
  // komt eraan: altijd zichtbaar, kort
  const komt=[...X.voorstellen.map(v=>({...v,_rv:1})),...X.komt];
  const rv=v=>`<details class="item"><summary><span class="meta"><span class="d">${fd(v.datum)}</span><span><span class="stip open"></span>Raadsvoorstel${v.behandeling?' · '+esc(v.behandeling.slice(0,70)):''}</span></span><span class="t">${esc(v.titel)}</span><span class="pijl" aria-hidden="true">›</span></summary><div class="ctx"><div><a href="${esc(v.url)}" target="_blank" rel="noopener">Open in iBabs</a></div></div></details>`;
  h+=kBlok('komt','','Komt eraan',`${nf(komt.length)} punten`,'',o=>kLijst('komt',komt,x=>x._rv?rv(x):kRij(x),'Niets in de komende tijd.',o),{kleur:'geel',open:true});
  // coalitieakkoord
  const AK=X.akkoord,AP=KAKK&&KAKK.dossiers&&KAKK.dossiers[d.slug]||[],DP=AK&&KAKK&&KAKK.domeinen&&KAKK.domeinen[AK.domein]||[],PT=AP.length?AP:DP;
  if(AK&&PT.length)h+=kBlok('akkoord','','Coalitieakkoord 2026–2030',`${PT.length} punten`,esc(PT[0].wat),
    o=>`<ul class="kakk">${PT.slice(0,o?99:3).map(x=>`<li>${esc(x.wat)} <a class="sub" href="${esc(x.url)}" target="_blank" rel="noopener">blz. ${x.blz}</a>${cl(x)}</li>`).join('')}</ul>${o?`<p class="sub" style="font-size:13px;margin-top:8px">‘Vaart maken’ van PRO, D66, VVD, CDA en Volt (juli 2026). AI-samenvatting met bij elk punt het letterlijke citaat. <a href="akkoord.html">Het hele akkoord in het kort</a></p>`:`<button type="button" class="kmeer" data-blok="akkoord">Toon alle ${PT.length}</button>`}`,{kleur:'blauw'});
  // 1 gezegd
  const F=A&&A.fracties,laatst=X.debatten[0];
  h+=kBlok('gezegd','1','Gezegd',`${nf(X.debatten.length)} debatten`,laatst?`Laatste: ${fd(laatst.datum)}, ${esc(laatst.punt.slice(0,80))}`:'',
    o=>kLijst('gezegd',X.debatten,kDebat,'Geen debatten bij dit filter.',o)+(o&&F&&F.punten&&F.punten.length?kBinnen(blok('kf','Wat de fracties vinden',`<p class="intro">${alinea(F.intro||[])}</p>`,F.punten.map(f=>`<div class="pt"><b>${esc(f.fractie)}</b> ${f.standpunten.map(x=>`${esc(x.wat.replace(/\.$/,''))} ${bron(x)}${cl(x)}`).join('; ')}</div>`).join(''),`Toon ${F.punten.length} fracties`,true)):''));
  // 2 besloten
  const S=X.stemmen;
  h+=kBlok('besloten','2','Besloten',`${nf(L.mot.length)} moties · ${nf(X.vastgesteld.length)} regels`,`Aangenomen moties, de stemming per fractie en de vastgestelde regels`,
    o=>`<h3>Aangenomen moties</h3>`+kLijst('besloten',L.mot,kRij,'Geen aangenomen moties bij dit filter.',o)+(o?kStemtabel()+`<h3 style="margin-top:24px">Vastgesteld in het Gemeenteblad</h3><div class="lijst">${X.vastgesteld.filter(x=>kIn('besloten',x)).slice(0,12).map(v=>`<div class="pt kvast"><span class="sub">${fd(v.datum)} · ${esc(v.soort)}${v.n>1?` · ${v.n} versies`:''}</span><br><a href="${esc(v.url)}" target="_blank" rel="noopener">${esc(v.titel)}</a></div>`).join('')||'<p class="leeg">Niets bij dit filter.</p>'}</div>`:''));
  // 3 beloofd
  const C=A&&A.college,bl={open:L.open,laat:L.laat}[KBEL]||L.open;
  h+=kBlok('beloofd','3','Beloofd',`${nf(L.open.length)} open${L.laat.length?`, ${nf(L.laat.length)} te laat`:''}`,'Toezeggingen en moties die nog uitgevoerd moeten worden, met het beloftespoor',
    o=>(o?`<div class="kfilter" role="group" aria-label="Status"><span class="sub">Status:</span>${[['open','Open',L.open.length],['laat','Over de termijn',L.laat.length]].map(([k,t,n])=>`<button type="button" data-bel="${k}" aria-pressed="${k===KBEL}">${t} (${n})</button>`).join('')}</div>`:'')+
      kLijst('beloofd',bl,kRij,'Niets in deze lijst.',o)+(o&&C&&C.punten&&C.punten.length?kBinnen(blok('kc','Wat het college beloofde en deed',`<p class="intro">${alinea(C.intro||[])}</p>`,C.punten.map(x=>`<div class="pt">${rijAI(x)}</div>`).join(''),`Toon ${C.punten.length} punten`,true)):''));
  // 4 gedaan
  const dl=L.af.map(x=>dagen(x.datum,x.stappen[x.stappen.length-1][0])).filter(v=>v>=0).sort((a,b)=>a-b),med=dl.length?dl[Math.floor(dl.length/2)]:null;
  h+=kBlok('gedaan','4','Gedaan',`${nf(L.af.length)} afgedaan`,med!==null?`Van belofte tot afdoening meestal ${med} dagen (mediaan)`:'',o=>kLijst('gedaan',L.af,kRij,'Nog niets afgedaan bij dit filter.',o));
  // in de stad
  const W=A&&A.wijken;
  h+=kBlok('stad','','In de stad',KPK?'kaart 2016–2026':'kaart',KPK?'Waar betaald parkeren geldt, door de jaren, en waar het nog komt':'Waar in Rotterdam het speelt, per wijk',
    o=>o?(KPK?kParkeerkaart():'')+kStadInhoud()+(W&&W.punten&&W.punten.length?kBinnen(blok('kw','Signalen uit de wijken',`<p class="intro">${alinea(W.intro||[])}</p>`,W.punten.map(x=>`<div class="pt"><b>${esc(x.wijk)}</b> ${rijAI(x)}</div>`).join(''),`Toon ${W.punten.length} signalen`,true)):'')
      :`<button type="button" class="kmeer" data-blok="stad">Open de kaart</button>`);
  // achtergrond
  const T=A&&A.tijdlijn,O=A&&A.open;
  h+=kBlok('achtergrond','','Achtergrond','het hele verhaal','Meer diepgang, tijdlijn, open eindjes en cijfers',o=>{if(!o)return `<button type="button" class="kmeer" data-blok="achtergrond">Lees het hele verhaal</button>`;let a='';
    if(A&&A.verdieping&&A.verdieping.length)a+=`<div class="verd">${A.verdieping.map(p=>`<p>${alinea(p)}</p>`).join('')}</div>`;
    if(T&&T.punten&&T.punten.length)a+=kBinnen(blok('kt','Tijdlijn',`<p class="intro">${alinea(T.intro||[])}</p>`,`<div class="tlr">${T.punten.map(x=>`<div class="d">${fd(x.bron_datum)}</div><div class="pt">${rijAI(x)}</div>`).join('')}</div><div style="margin-top:16px">${tijdlijnSvg(d)}</div>`,`Toon ${T.punten.length} momenten en de grafiek`,true));
    if(O&&O.punten&&O.punten.length)a+=kBinnen(blok('ko','Open eindjes',`<p class="intro">${alinea(O.intro||[])}</p>`,O.punten.map(x=>`<div class="pt">${rijAI(x)}</div>`).join(''),`Toon ${O.punten.length} punten`,true));
    a+=kBinnen(blok('kcij','Cijfers',`<p class="intro">Aandacht per jaar en wie erover praat.</p>`,`<div class="cijferblok" style="margin-top:16px"><section class="grafiek"><h3>Aandacht per jaar</h3>${trendSvg(d)}<p class="sub">${d.eenheid==='procent'?'Aandeel van alle gesproken woorden in de raad, in procenten.':'Keren genoemd per 100.000 gesproken woorden in de raad.'}</p></section><section><h3>Wie praat erover?</h3><div class="balken">${d.partijen.slice(0,8).map(p=>`<div class="balk2"><span>${esc(p[0])}</span><i style="width:${p[1]/Math.max(...d.partijen.map(q=>q[1]))*100}%"></i><span class="v num">${String(p[1]).replace('.',',')}</span></div>`).join('')}</div><p class="sub" style="margin-top:8px">Geen oordeel; alleen hoe vaak het onderwerp terugkomt.</p></section></div>`,'Toon cijfers'));
    return a;});
  $('kinh').innerHTML=h;
  if(KOPEN.has('stad')){kKaart();kPkTeken();}
}
function kStadInhoud(){
  const X=KX;
  return `<h3 style="margin-top:${KPK?24:0}px">Waar de raad het over had</h3><p class="sub" style="margin:0 0 8px">Stukken en debatten die de wijk noemen of uit de wijk komen. Klik op een wijk${(X.projecten||[]).length?' of een project (●)':''}.</p>`+
    ((X.lagen||[]).length?`<div class="klagen" role="group" aria-label="Kaartlaag">${X.lagen.map(([id,t])=>`<button type="button" data-laag="${id}" aria-pressed="${id===KLAAG}">${esc(t)}</button>`).join('')}</div>
      <div class="kjaar" id="kjaar" ${KLAAG==='vg'?'':'hidden'}><label for="kjr">Jaar</label><input type="range" id="kjr" min="2018" max="2026" step="1" value="${KJR==='alle'?2026:KJR}"><b id="kjrv">${KJR==='alle'?'alle jaren':KJR}</b><button type="button" class="knop wit klein" id="kspeel">▶ Afspelen</button><button type="button" class="wis" id="kalle">alle jaren</button></div>`:'')+
    `<div class="kstad"><div class="kkaart" id="kkaart"></div><div id="kwijk"><p class="sub">Klik op een wijk op de kaart.</p></div></div>`+
    ((X.projecten||[]).length?`<h3 style="margin-top:20px">Grote projecten</h3><div class="kproj">${X.projecten.map((p,i)=>{const J=['2018','2019','2020','2021','2022','2023','2024','2025','2026'],m=Math.max(1,...J.map(j=>p.per[j]||0));
      return `<button type="button" class="kp" data-proj="${i}"><b>${esc(p.naam)}</b><span class="sub">${esc(p.wijknaam)} · ${nf(p.n)} stukken</span><span class="kspark" aria-hidden="true">${J.map(j=>`<i style="height:${Math.max(2,(p.per[j]||0)/m*22)}px" title="${j}: ${p.per[j]||0}"></i>`).join('')}</span></button>`;}).join('')}</div>`:'');
}
/* ---------- stemtabel: per motie hoe elke fractie stemde ---------- */
function kStemtabel(){
  const S=KX.stemmen;if(!S||!(S.tabel||[]).length)return '';
  const rij=S.tabel.filter(r=>!KSUB.besloten||(r[5]||[]).includes(KSUB.besloten));
  const tel={};rij.forEach(r=>Object.keys(r[4]).forEach(p=>tel[p]=(tel[p]||0)+1));
  const fr=Object.keys(tel).filter(p=>tel[p]>=Math.max(2,rij.length*.3)).sort((a,b)=>a.localeCompare(b));
  if(!rij.length||!fr.length)return '';
  return `<h3 style="margin-top:24px">Hoe stemden de fracties?</h3><p class="sub" style="margin:4px 0 8px">${rij.length} moties met een hoofdelijke stemming sinds 2022, nieuwste boven. <span class="sv v">✓</span> voor, <span class="sv t">✗</span> tegen, leeg = niet in de raad of niet geteld. Fracties op alfabet.</p>
    <div class="kstab"><table><thead><tr><th>Motie</th>${fr.map(p=>`<th><span>${esc(p)}</span></th>`).join('')}</tr></thead><tbody>${rij.map(r=>`<tr><th><a href="${esc(r[2])}" target="_blank" rel="noopener">${esc(r[1])}</a><span class="sub">${fd(r[0])} · ${r[3]?'aangenomen':'verworpen'}</span></th>${fr.map(p=>`<td>${r[4][p]==='v'?'<span class="sv v" title="voor">✓</span>':r[4][p]==='t'?'<span class="sv t" title="tegen">✗</span>':''}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
}
/* ---------- parkeerkaart: betaald parkeren door de jaren (RDW) ---------- */
let PJR='2026',PSPEEL=null;
function kParkeerkaart(){
  const P=KPK,s=P.stat;
  const mx=Math.max(...P.jaren.map(j=>s[j].max||0)),W=420,H=140,bw=(W-30)/P.jaren.length;let g='';
  P.jaren.forEach((j,i)=>{const v=s[j].mediaan||0,x=26+bw*i,hh=100*v/mx;g+=`<rect x="${x+bw*.2}" y="${112-hh}" width="${bw*.6}" height="${hh}" fill="${j===PJR?'#004C31':'#4EB051'}"><title>${j}: ${s[j].zones} zones, middentarief € ${String(v).replace('.',',')} per uur</title></rect><text x="${x+bw/2}" y="128" font-size="10" text-anchor="middle">'${j.slice(2)}</text>`;});
  for(let t=0;t<=mx;t+=1)g+=`<text x="20" y="${112-100*t/mx+4}" font-size="10" text-anchor="end">€${t}</text><line x1="24" x2="${W}" y1="${112-100*t/mx}" y2="${112-100*t/mx}" stroke="#EFF4F6"/>`;
  return `<div class="pk"><div class="pkkop"><h3>Betaald parkeren door de jaren</h3><div class="kjaar"><label for="pjr">Jaar</label><input type="range" id="pjr" min="${P.jaren[0]}" max="${P.jaren[P.jaren.length-1]}" step="1" value="${PJR}"><b id="pjrv">${PJR}</b><button type="button" class="knop wit klein" id="pspeel">▶ Afspelen</button></div></div>
    <div class="pkgrid"><div class="kkaart" id="pkkaart"></div><div><p class="pkstat" id="pkstat"></p>
      <div class="pkleg"><span><i style="background:#00811F"></i>betaald parkeren (donkerder = duurder)</span><span><i class="arc"></i>komt er volgens het Kader 2026 bij</span><span><i style="background:#DBE7EA"></i>uitgezonderd: kleine kernen</span></div>
      <h3 style="margin-top:16px;font-size:15px">Wat kost een uur? (middentarief, woensdag 12 uur)</h3><svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Middentarief per jaar">${g}</svg>
      <p class="sub" style="font-size:12px">${esc(P.kader.tekst)} <a href="${esc(P.kader.url)}" target="_blank" rel="noopener">Het kader</a>. Bron zones en tarieven: ${esc(P.bron)}.</p></div></div></div>`;
}
function kPkTeken(){
  if(!KPK||!$('pkkaart')||!KWK||!KKAART)return;
  const P=KPK,j=PJR,zs=P.zones.filter(z=>z.jaren[j]!==undefined),tar=zs.map(z=>z.jaren[j]).filter(v=>v>0),mx=Math.max(1,...tar),mn=Math.min(...tar,mx);
  const kl=v=>{if(!v)return '#99CCA0';const f=(v-mn)/Math.max(.01,mx-mn);return f>.75?'#004C31':f>.5?'#006E32':f>.25?'#00811F':'#4EB051';};
  const st=P.wijken;
  $('pkkaart').innerHTML=`<svg viewBox="0 0 ${KKAART.w} ${KKAART.h}" role="img" aria-label="Betaald parkeren in ${j}"><defs><pattern id="arc" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="6" height="6" fill="#FFF4CC"/><line x1="0" y1="0" x2="0" y2="6" stroke="#E56E02" stroke-width="2"/></pattern></defs>
    <path d="${KKAART.havens}" fill="#EFF4F6"/>${KWK.wijken.map(w=>{const s=st[w.slug];return `<path d="${w.d}" fill="${s==='gepland'&&j==='2026'?'url(#arc)':s==='uitgezonderd'?'#DBE7EA':'#F3F8F3'}" stroke="#fff" stroke-width=".6"><title>${esc(w.naam)}${s==='gepland'?': betaald parkeren gepland (Kader 2026)':s==='uitgezonderd'?': uitgezonderd':''}</title></path>`;}).join('')}
    ${zs.map(z=>`<path d="${z.d}" fill="${kl(z.jaren[j])}" fill-opacity=".9" stroke="#fff" stroke-width=".3"><title>${esc(z.naam||'zone '+z.id)}: ${z.jaren[j]?'€ '+String(z.jaren[j]).replace('.',',')+' per uur':'betaald parkeren'} (${j})</title></path>`).join('')}
    <path d="${KKAART.water}" fill="#CFE3EF" pointer-events="none"/></svg>`;
  const s=P.stat[j],s0=P.stat[P.jaren[0]];
  $('pkstat').innerHTML=`<b class="num" style="font-size:28px">${s.zones}</b> zones met betaald parkeren in ${j}${j!==P.jaren[0]?` <span class="sub">(${P.jaren[0]}: ${s0.zones})</span>`:''}<br>middentarief <b>€ ${String(s.mediaan||0).replace('.',',')}</b> per uur${s.max?`, duurste zone € ${String(s.max).replace('.',',')}`:''}${j==='2026'?`<br><span class="sub">In ${Object.values(P.wijken).filter(x=>x==='gepland').length} wijken komt het er nog bij (gearceerd).</span>`:''}`;
  document.querySelectorAll('#k-stad .pk svg rect').forEach(r=>{const t=r.querySelector('title');if(t)r.setAttribute('fill',t.textContent.startsWith(j)?'#004C31':'#4EB051');});
}
let KLAAG='n',KJR='alle',KSPEEL=null;
function kWaarde(w){
  if(KLAAG==='n')return Object.values(w.n||{}).reduce((a,b)=>a+b,0);
  if(KLAAG==='vg')return KJR==='alle'?Object.values(w.vg||{}).reduce((a,b)=>a+b,0):((w.vg||{})[KJR]||0);
  return w[KLAAG];
}
const kCbs=()=>{const l=(KX.lagen||[]).find(x=>x[0]===KLAAG);return !!l&&/CBS/.test(l[2]);};
function kKaart(){
  if(!KWK||!KKAART||!$('kkaart'))return;
  const per=Object.fromEntries(KX.wijken.map(w=>[w.slug,w])),vals=KX.wijken.map(kWaarde).filter(v=>v!=null),mx=Math.max(1,...vals),mn=kCbs()?Math.min(...vals):0;
  const f=v=>v==null?null:(v-mn)/Math.max(1e-9,mx-mn),kl=x=>x==null?'#EFF4F6':x>.8?'#004C31':x>.6?'#00811F':x>.4?'#4EB051':x>.2?'#99CCA0':'#E1EFE2';
  const laag=(KX.lagen||[]).find(l=>l[0]===KLAAG);
  const proj=(KX.projecten||[]).map((p,i)=>`<g class="kpm" data-proj="${i}" tabindex="0" role="button" aria-label="${esc(p.naam)}"><circle cx="${p.lx}" cy="${p.ly}" r="${(4+Math.sqrt(p.n)/2).toFixed(1)}" fill="#00548F" fill-opacity=".85" stroke="#fff" stroke-width="1.5"/><title>${esc(p.naam)}: ${p.n} stukken</title></g>`).join('');
  $('kkaart').innerHTML=`<svg viewBox="0 0 ${KKAART.w} ${KKAART.h}" role="img" aria-label="Kaart van Rotterdam per wijk"><path class="h" d="${KKAART.havens}"/>${KWK.wijken.map(w=>{const x=per[w.slug],v=x?kWaarde(x):null;
    return `<path class="wk" data-w="${w.slug}" d="${w.d}" tabindex="0" fill="${kl(f(v))}"><title>${esc(w.naam)}: ${v==null?'geen gegevens':nf(Math.round(v*10)/10)}</title></path>`;}).join('')}<path class="w" d="${KKAART.water}"/>${proj}</svg>
    <p class="sub" style="margin-top:6px">${laag?esc(laag[1])+': '+esc(laag[2])+'. ':''}Donkerder = meer${kCbs()?'; cijfers ter vergelijking, geen oordeel':'. Aantallen zijn een indicatie: ‘genoemd in’ klopt in ongeveer 9 van de 10 gevallen'}.</p>`;
}
function kWijk(s){
  const x=KX.wijken.find(w=>w.slug===s);if(!x)return;
  document.querySelectorAll('#kkaart path.wk').forEach(p=>p.classList.toggle('sel',p.dataset.w===s));
  const t={raad:'raadsstukken en debatten die de wijk noemen',wijkraad:'stukken van de wijkraad',verkeersbesluit:'verkeersbesluiten',besluit:'andere besluiten'};
  const vg=x.vg?Object.values(x.vg).reduce((a,b)=>a+b,0):null;
  $('kwijk').innerHTML=`<h3>${esc(x.naam)} <span class="sub">· ${esc(x.gebied)}</span></h3>
    <ul class="kn">${Object.entries(t).filter(([k])=>(x.n||{})[k]).map(([k,l])=>`<li><b class="num">${nf(x.n[k])}</b> ${l}</li>`).join('')}${vg!=null?`<li><b class="num">${nf(vg)}</b> ${esc(((KX.lagen||[]).find(l=>l[0]==='vg')||[,'vergunningen'])[1].toLowerCase())} sinds 2018</li>`:''}</ul>
    ${(KX.lagen||[]).filter(l=>/CBS/.test(l[2])&&x[l[0]]!=null).length?`<p class="sub" style="margin:8px 0 0">Ter vergelijking (CBS 2024): ${(KX.lagen||[]).filter(l=>/CBS/.test(l[2])&&x[l[0]]!=null).map(l=>`${esc(l[1].toLowerCase())}: ${nf(x[l[0]])}`).join(' · ')}.</p>`:''}
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
/* ---------- bediening ---------- */
function kZet(id,open){if(open)KOPEN.add(id);else KOPEN.delete(id);history.replaceState(null,'','#'+KD.slug+(open?'/'+id:''));}
function kHerteken(anker){const el=anker&&$('k-'+anker),y=el?el.getBoundingClientRect().top:0;kTeken();const n=anker&&$('k-'+anker);if(n)window.scrollBy(0,n.getBoundingClientRect().top-y);}
document.addEventListener('click',e=>{
  if(!KX||!$('kinh'))return;
  const b=e.target.closest('[data-blok]');if(b){const id=b.dataset.blok,open=!KOPEN.has(id)||b.classList.contains('kmeer');kZet(id,open);kHerteken(id);if(open&&b.classList.contains('kmeer'))$('k-'+id).scrollIntoView({block:'start',behavior:'smooth'});return;}
  const o=e.target.closest('[data-openen]');if(o){e.preventDefault();kZet(o.dataset.openen,true);kTeken();$('k-'+o.dataset.openen).scrollIntoView({block:'start',behavior:'smooth'});return;}
  const f=e.target.closest('[data-ksub]');if(f){const [id,v]=f.dataset.ksub.split('|');KSUB[id]=v;kHerteken(id);return;}
  const bl=e.target.closest('[data-bel]');if(bl){KBEL=bl.dataset.bel;kHerteken('beloofd');return;}
  const w=e.target.closest('#kkaart path.wk');if(w){kWijk(w.dataset.w);return;}
  const pj=e.target.closest('[data-proj]');if(pj){kProj(+pj.dataset.proj);return;}
  const lg=e.target.closest('[data-laag]');if(lg){KLAAG=lg.dataset.laag;document.querySelectorAll('[data-laag]').forEach(x=>x.setAttribute('aria-pressed',x===lg));$('kjaar').hidden=KLAAG!=='vg';kKaart();return;}
  if(e.target.id==='kalle'){KJR='alle';$('kjrv').textContent='alle jaren';kKaart();return;}
  if(e.target.id==='kspeel'){if(KSPEEL){clearInterval(KSPEEL);KSPEEL=null;e.target.textContent='▶ Afspelen';return;}
    let j=2018;e.target.textContent='❚❚ Stop';const stap=()=>{KJR=String(j);$('kjr').value=j;$('kjrv').textContent=j;kKaart();j++;if(j>2026){clearInterval(KSPEEL);KSPEEL=null;e.target.textContent='▶ Afspelen';}};stap();KSPEEL=setInterval(stap,900);return;}
  if(e.target.id==='pspeel'){if(PSPEEL){clearInterval(PSPEEL);PSPEEL=null;e.target.textContent='▶ Afspelen';return;}
    const J=KPK.jaren;let i=0;e.target.textContent='❚❚ Stop';const stap=()=>{PJR=J[i];$('pjr').value=PJR;$('pjrv').textContent=PJR;kPkTeken();i++;if(i>=J.length){clearInterval(PSPEEL);PSPEEL=null;e.target.textContent='▶ Afspelen';}};stap();PSPEEL=setInterval(stap,900);return;}
  const v=e.target.closest('[data-video]');if(v){kVideo(v.dataset.video,+v.dataset.sec,v.dataset.titel);}
});
document.addEventListener('input',e=>{if(e.target.id==='kjr'){KJR=e.target.value;$('kjrv').textContent=KJR;kKaart();}if(e.target.id==='pjr'){PJR=e.target.value;$('pjrv').textContent=PJR;kPkTeken();}});
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
