/* Gedeeld door de ontwerpschermen: kop, hulpfuncties, zoeklijst (combobox), uitklapbare rijen, deellinks. */
const $=id=>document.getElementById(id);
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const nf=n=>Number(n).toLocaleString('nl-NL');
const MND=['jan','feb','mrt','apr','mei','jun','jul','aug','sep','okt','nov','dec'];
const MNDL=['januari','februari','maart','april','mei','juni','juli','augustus','september','oktober','november','december'];
const fd=d=>{if(!d)return '';const [y,m,dd]=d.split('-');return +dd+' '+MND[+m-1]+' '+y;};
const fdl=d=>{const [y,m,dd]=d.split('-');return +dd+' '+MNDL[+m-1]+' '+y;};
const slug=s=>s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/&/g,' ').replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
const iso=s=>{const m=(s||'').match(/(\d\d)-(\d\d)-(\d{4})/);return m?`${m[3]}-${m[2]}-${m[1]}`:'';};
const FREQ='Wordt automatisch bijgewerkt: elke nacht, en op werkdagen om 9, 12, 15, 18 en 21 uur.';
const STAND='2026-10-05';   /* stand van de gegevens; ook in src/paden.py */
const dagen=(a,b)=>Math.round((new Date(b)-new Date(a))/864e5);

/* logo: halfrond van negen zetels (de raadzaal), één groen gemarkeerd; woordmerk in kleine letters */
const LOGO=(kleur='#fff',accent='#fff')=>{let s='';const n=9;for(let i=0;i<n;i++){const a=Math.PI*(1-i/(n-1)),x=17+13*Math.cos(a),y=18-13*Math.sin(a);s+=`<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="2.6" fill="${i===6?accent:kleur}" ${i===6?'':'opacity=".75"'}/>`;}
  return `<svg viewBox="0 0 34 20" aria-hidden="true">${s}<circle cx="17" cy="17" r="3.2" fill="${kleur}"/></svg>`;};
function kop(actief){
  const m=[['zoeken','Zoeken','zoek.html'],['vergaderingen','Vergaderingen','vergaderingen.html'],['domeinen','Domeinen','domeinen.html'],['gebieden','Gebieden','wijk.html']];
  const r=[['verkenner','Verkenner','verkenner.html'],['lab','Inzichten','lab.html'],['over','Over','over.html']];
  const a=x=>`<a href="${x[2]}" class="${x[0]===actief?'on':''}"${x[0]===actief?' aria-current="page"':''}>${x[1]}</a>`;
  document.querySelector('header.balk').innerHTML=`<div class="in"><a class="merk" href="startpagina.html" aria-label="raadzoeker, naar de startpagina">${LOGO()}<b>raadzoeker</b><small>onofficieel</small></a>
    <nav aria-label="Hoofdmenu">${m.map(a).join('')}</nav><nav class="rechts" aria-label="Over en experimenten">${r.map(a).join('')}<a class="bijgewerkt" id="bijgewerkt" href="over.html#actueel" title="${esc(FREQ)}">gegevens t/m ${fd(STAND)}</a></nav></div>`;
  // laatste automatische update (status.json schrijft de NAS na elke geslaagde run)
  fetch('../data/status.json',{cache:'no-store'}).then(r=>r.ok?r.json():null).then(st=>{if(!st||!st.laatste)return;const el=document.getElementById('bijgewerkt');if(!el)return;
    const d=new Date(st.laatste);el.textContent='bijgewerkt '+d.getDate()+' '+MND[d.getMonth()]+' '+String(d.getHours()).padStart(2,'0')+':'+String(d.getMinutes()).padStart(2,'0');}).catch(()=>{});
  // rondleiding, hulpknop en welkomstvenster (tour.js)
  if(!document.getElementById('rz-tour')){const t=document.createElement('script');t.id='rz-tour';t.src='tour.js?v=8';document.body.appendChild(t);const w=document.createElement('script');w.src='woorden.js?v=3';document.body.appendChild(w);const r=document.createElement('script');r.src='stad.js?v=3';document.body.appendChild(r);}
  const ic=document.createElement('link');ic.rel='icon';ic.href='data:image/svg+xml,'+encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 34 34"><rect width="34" height="34" rx="7" fill="#00811F"/><g transform="translate(0,7)">${LOGO().replace(/<\/?svg[^>]*>/g,'')}</g></svg>`);document.head.appendChild(ic);
}
/* zoeken in onderwerpen of gebieden; kiezen roept kies(d) aan */
/* bewerkingsafstand (Levenshtein), voor 'bedoel je…' bij tikfouten */
function afstand(a,b){if(Math.abs(a.length-b.length)>3)return 9;let v=[...Array(b.length+1).keys()];for(let i=1;i<=a.length;i++){let p=v[0];v[0]=i;for(let j=1;j<=b.length;j++){const t=v[j];v[j]=Math.min(v[j]+1,v[j-1]+1,p+(a[i-1]===b[j-1]?0:1));p=t;}}return v[b.length];}
/* beste 'bedoel je…' uit een lijst namen: per woord vergelijken, tolerantie naar woordlengte */
function bedoelJe(q,namen,n=3){q=q.toLowerCase().trim();if(q.length<3)return[];
  return namen.map(x=>{const w=x.toLowerCase().split(/[^a-z0-9à-ÿ]+/).filter(Boolean);const d=Math.min(...w.map(y=>afstand(q,y.slice(0,Math.max(q.length,y.length)))),afstand(q,x.toLowerCase()));return [d,x];})
    .filter(([d])=>d<=(q.length<6?1:2)).sort((a,b)=>a[0]-b[0]).slice(0,n).map(x=>x[1]);}
function zoeklijst(input,lijst,bron,kies){
  let hits=[],act=0;
  const toon=()=>{lijst.innerHTML=hits.length?hits.map((d,i)=>`<li role="option" id="opt${i}" aria-selected="${i===act}" data-i="${i}">${esc(d.naam)} <span class="sub">· ${esc(d.groep)}</span></li>`).join(''):leegLijst();
    lijst.classList.add('on');input.setAttribute('aria-expanded','true');input.setAttribute('aria-activedescendant',hits.length?'opt'+act:'');};
  const leegLijst=()=>{const q=input.value.trim(),b=bedoelJe(q,bron().map(d=>d.naam));
    return `<li class="leeg" role="option" aria-disabled="true">Geen dossier met die naam.${b.length?` Bedoel je ${b.map(x=>`<a href="#" data-bedoel="${esc(x)}">${esc(x)}</a>`).join(' of ')}?`:''} <a href="zoek.html?q=${encodeURIComponent(q)}">Zoek '${esc(q)}' in alles wat er gezegd en geschreven is →</a></li>`;};
  lijst.addEventListener('mousedown',e=>{const a=e.target.closest('[data-bedoel]');if(!a)return;e.preventDefault();input.value=a.dataset.bedoel;input.dispatchEvent(new Event('input'));});
  const sluit=()=>{lijst.classList.remove('on');input.setAttribute('aria-expanded','false');};
  input.addEventListener('input',()=>{const q=input.value.trim().toLowerCase();if(!q){sluit();return;}
    hits=bron().map(d=>{const n=d.naam.toLowerCase();return [n.startsWith(q)?3:n.includes(q)?2:d.sub.some(x=>x.toLowerCase().includes(q))?1.5:d.termen.toLowerCase().includes(q)?1:0,d];}).filter(x=>x[0]).sort((a,b)=>b[0]-a[0]).slice(0,10).map(x=>x[1]);act=0;toon();});
  input.addEventListener('keydown',e=>{if(!lijst.classList.contains('on'))return;
    if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();if(hits.length){act=(act+(e.key==='ArrowDown'?1:-1)+hits.length)%hits.length;toon();}}
    else if(e.key==='Enter'&&hits[act]){e.preventDefault();sluit();input.value='';kies(hits[act]);}
    else if(e.key==='Escape')sluit();});
  lijst.addEventListener('click',e=>{const li=e.target.closest('[data-i]');if(li){sluit();input.value='';kies(hits[+li.dataset.i]);}});
  document.addEventListener('click',e=>{if(!e.target.closest('.zoekveld'))sluit();});
}
/* onderwerp/gebied zoeken op #slug of #nummer */
function uitHash(lijst){const h=decodeURIComponent(location.hash.slice(1));if(!h)return null;return lijst.find(d=>slug(d.naam)===h)||(/^\d+$/.test(h)?lijst.find(d=>d.id===+h):null);}

/* uitklapbare rij voor een motie, toezegging of ander stuk
   r=[datum,titel,indiener,statustekst,url,bb,context] ; soort='motie'|'toez'|'stuk' ; stand=peildatum */
function rij(r,soort,stand){
  const dl=iso((r[3].match(/verwacht ([\d-]+)/)||[])[1]),af=iso((r[3].match(/afgedaan ([\d-]+)/)||[])[1]);
  const laat=dl&&!af&&dl<stand,isAf=/afgedaan(?! )|afgedaan \d/.test(r[3])&&!/nog niet afgedaan/.test(r[3]);
  const status=isAf?`<span><span class="stip af"></span>Afgedaan${af?' op '+fd(af):''}</span>`:laat?`<span><span class="stip laat"></span>${dagen(dl,stand)} dagen over de termijn</span>`:dl?`<span><span class="stip open"></span>Afdoening verwacht ${fd(dl)}</span>`:r[3]?`<span>${esc(r[3])}</span>`:'';
  const c=r[6]||{};let ctx='';
  if(c.s)ctx+=stemHTML(c.s);
  if(c.c)ctx+=`<div><b>Aanleiding</b> ‘${esc(c.c)}’</div>`;
  if(c.v)ctx+=`<div><b>Verzoek aan het college</b> ‘${esc(c.v)}’</div>`;
  if(c.o)ctx+=`<div><b>Toegezegd</b> ‘${esc(c.o)}’</div>`;
  ctx+=`<div><a href="${esc(r[4])}" target="_blank" rel="noopener">Open in iBabs${r[5]?' ('+esc(r[5])+')':''}</a></div>`;
  return `<details class="item"><summary><span class="meta"><span class="d">${fd(r[0])}</span>${status}${r[2]?`<span class="wie">${esc(r[2])}</span>`:''}</span><span class="t">${esc(r[1])}</span><span class="pijl" aria-hidden="true">›</span></summary><div class="ctx">${ctx}</div></details>`;
}
/* debat met letterlijk fragment: x=[datum,agendaId,titel,treffers,fragment,start,lengte,sprekers,soort] */
function debatRij(x,termen){
  const f=x[4]||'',a=x[5],l=x[6];const fr=a>=0?esc(f.slice(0,a))+'<mark>'+esc(f.slice(a,a+l))+'</mark>'+esc(f.slice(a+l)):esc(f);
  const archief=`zoek.html#q=${encodeURIComponent(termen)}&van=${x[0].slice(0,4)}&tot=${x[0].slice(0,4)}`;
  return `<details class="item"><summary><span class="meta"><span class="d">${fd(x[0])}</span><span>${nf(x[3])} ${x[5]<0?'spreekbeurten':'keer genoemd'}</span>${x[7]&&x[7].length?`<span class="wie">${esc(x[7].join(', '))}</span>`:''}</span><span class="t">${esc(x[2]||'Raadsvergadering')}</span><span class="pijl" aria-hidden="true">›</span></summary>
    <div class="ctx"><div>‘${fr}’${x[8]===4?' <span class="sub">(automatische ondertiteling)</span>':''}</div>
    <div><a href="${archief}">Lees het debat</a> · <a href="https://gemeenteraad.rotterdam.nl/Agenda/Index/${esc(x[1])}" target="_blank" rel="noopener">Vergadering en video in iBabs</a></div></div></details>`;
}
/* deellinks: e-mail, Teams, WhatsApp en kopiëren */
function deel(el,titel,url){
  const u=encodeURIComponent(url),t=encodeURIComponent(titel);
  el.innerHTML=`<span class="sub">Delen:</span> <a href="mailto:?subject=${t}&body=${t}%0A${u}">E-mail</a> · <a href="https://teams.microsoft.com/share?href=${u}&msgText=${t}" target="_blank" rel="noopener">Teams</a> · <a href="https://wa.me/?text=${t}%20${u}" target="_blank" rel="noopener">WhatsApp</a> · <button type="button" class="kopie" style="font:inherit;background:none;border:0;padding:0;text-decoration:underline;cursor:pointer">Kopieer link</button>`;
  el.querySelector('.kopie').addEventListener('click',e=>{navigator.clipboard.writeText(url).then(()=>{e.target.textContent='Link gekopieerd';},()=>{prompt('Kopieer deze link',url);});});
}

/* stemhalfrond: 45 zetels, voor groen, tegen grijs; s=[aangenomen,voor,tegen,zijde,fracties] uit de notulen */
const ZETELS=(()=>{const rij=[[1,15],[.84,12],[.68,10],[.52,8]],z=[];for(const [r,n] of rij)for(let i=0;i<n;i++){const a=Math.PI*(1-i/(n-1));z.push([a,60+52*r*Math.cos(a),58-52*r*Math.sin(a)]);}return z.sort((p,q)=>q[0]-p[0]);})();
function stemHTML(s){
  const [aan,voor,tegen,zijde,fr]=s;
  if(voor<0)return `<div><b>Stemming</b> ${aan?'Aangenomen':'Verworpen'} zonder hoofdelijke telling (meestal: met algemene stemmen of zonder stemming).</div>`;
  const tot=voor+tegen;let dots='';ZETELS.forEach((z,i)=>{const kl=i<voor?'#00811F':i<tot?'#65757C':'#DBE7EA';dots+=`<circle cx="${z[1].toFixed(1)}" cy="${z[2].toFixed(1)}" r="2.9" fill="${kl}"/>`;});
  return `<div style="display:flex;gap:16px;align-items:center;flex-wrap:wrap"><svg viewBox="0 0 120 62" width="132" height="68" role="img" aria-label="${voor} voor, ${tegen} tegen">${dots}</svg>
    <div><b>${aan?'Aangenomen':'Verworpen'}</b> met <span class="num">${voor}</span> stemmen voor en <span class="num">${tegen}</span> tegen.${fr?`<br><span class="sub">${zijde==='v'?'Voor':'Tegen'} stemden: ${esc(fr)}.</span>`:''}</div></div>`;
}
