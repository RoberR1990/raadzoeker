function zoomHTML(){
  const cur=TSTR[$('q').value.trim()];if(!cur)return '';
  const th=cur.th;
  return '<div class="zoom"><span class="zl">Thema <b>'+esc(th[0])+'</b>'+(th[2].length?' · zoom in:':'')+'</span>'+(th[2].length?'<button type="button" class="chip'+(cur.sub<0?' on':'')+'" data-theme="'+esc(th[1])+'">Alles</button>'+th[2].map((s,k)=>'<button type="button" class="chip'+(cur.sub===k?' on':'')+'" data-theme="'+esc(s[1])+'" title="'+esc(s[1])+'">'+esc(s[0])+'</button>').join(''):'')+'</div>';
}
function renderBrowse(){
  const T=META.tot||{},mln=n=>(n/1e6).toFixed(1).replace('.',',')+' mln';
  let h=tabsHTML()+'<section class="hero"><div class="hl"><h2>Wat is er in de Rotterdamse raad gezegd?</h2>'+
   '<p class="lead">Doorzoek letterlijk wat raadsleden, wethouders en de burgemeester sinds 2018 in de gemeenteraad hebben gezegd. Vind het citaat, zie wie het zei, lees het debat eromheen en kopieer het met bron.</p>'+
   '<div class="try">Probeer: <a data-theme="parkeernorm">parkeernorm</a><a data-theme="betaald parkeren">betaald parkeren</a><a data-theme="zeg ik toe | zeg ik u toe | toezegging | kan ik toezeggen | zeggen wij toe">toezeggingen</a><a data-theme="&quot;ai&quot; | algoritme">AI | algoritme</a><a data-theme="spreidingswet">spreidingswet</a></div></div>'+
   '<div class="stats"><div><b>'+nf(T.sp||0)+'</b><span>spreekbeurten</span></div><div><b>'+mln(T.words||0)+'</b><span>gesproken woorden</span></div><div><b>'+nf((T.verg||0)+(T.auto||0))+'</b><span>vergaderingen</span></div><div><b>'+nf(T.moties||0)+'</b><span>stemmingen</span></div></div></section>';
  h+='<div class="how">'+
   '<button type="button" data-focus="1"><i>1</i><b>Zoek letterlijk</b><span>Typ een woord of zin in de zoekbalk. Met | zoek je meerdere termen tegelijk; filter daarna op spreker, partij, rol, datum of agendapunt.</span></button>'+
   '<button type="button" data-scroll="themas"><i>2</i><b>Volg een thema</b><span>26 thema’s met kant-en-klare zoektermen. Per beleidsdomein zoom je verder in op deelonderwerpen.</span></button>'+
   '<button type="button" data-view="m"><i>3</i><b>Bekijk stemmingen</b><span>'+nf(T.moties||0)+' moties, amendementen en voorstellen: aangenomen of verworpen, met stemverhouding.</span></button>'+
   '<button type="button" data-view="i"><i>4</i><b>Ontdek patronen</b><span>Welke thema’s leven wanneer, en welke fractie heeft het waarover? Bekijk de warmtekaarten.</span></button></div>';
  h+='<h2 class="sec" id="themas">Thema’s</h2><div class="themes">'+THEMES.map(g=>'<div class="tg"><h3>'+g[0]+'</h3><div class="chips">'+g[1].map(t=>'<button type="button" class="chip" data-theme="'+esc(t[1])+'" title="'+esc(t[1])+'">'+esc(t[0])+(t[2].length?' <small>'+t[2].length+'</small>':'')+'</button>').join('')+'</div></div>').join('')+'</div>';
  h+='<h2 class="sec">Vergaderingen</h2>';
  Y.forEach((D,k)=>{
    const ms=D.M.map((m,i)=>i).sort((a,b)=>D.M[a][0]<D.M[b][0]?1:-1);
    h+='<details class="yr"'+(k===0?' open':'')+'><summary>'+D.y+' <small>'+D.M.length+' vergaderingen · '+nf(D.nSp)+' spreekbeurten</small></summary>';
    for(const mi of ms){const m=D.M[mi];
      h+='<details class="mt" data-m="'+D.y+':'+mi+'"><summary><span class="date">'+fdate(m[0])+'</span>'+(m[2]&&m[2]!=='Gemeenteraad'?'<span>'+esc(m[2])+'</span>':'')+
        (m[3]===1?'<span class="sub">'+nf(D.mc[mi])+' spreekbeurten</span>':m[3]===2?'<span class="tag warn">nog geen notulen · automatische ondertiteling</span>':'<span class="tag warn">nog geen notulen · sprekerstijdlijn</span>')+'</summary></details>';}
    h+='</details>';
  });
  if(!Y.length)h+='<div class="empty">Bezig met laden…</div>';
  h+='<section class="about" id="over"><h2>Over de Raadzoeker</h2><div class="ab">'+
   '<div><h3>Wat is het</h3><p>Een zoekmachine voor wat er letterlijk in de Rotterdamse gemeenteraad is gezegd, bedoeld voor beleidsmedewerkers en andere collega’s die willen weten wat de raad over hun onderwerp heeft besproken. Alles zit in dit ene bestand: je hebt geen account of installatie nodig, alleen voor de video is internet nodig.</p></div>'+
   '<div><h3>Waar komt de data vandaan</h3><p>Alles komt uit het openbare raadsinformatiesysteem van de gemeenteraad (<a href="'+SRC+'" target="_blank" rel="noopener">gemeenteraad.rotterdam.nl</a>, iBabs): de woordelijke notulen van '+nf(T.verg||0)+' raadsvergaderingen sinds 2018 (pdf), de agenda’s met sprekerstijdlijn, en de automatische ondertiteling van de uitzendingen. Stand: '+fdate(META.built,true)+'.</p></div>'+
   '<div><h3>Hoe is het gemaakt</h3><p>De notulen zijn automatisch opgeknipt per spreekbeurt en gekoppeld aan spreker, partij, rol en agendapunt. Motieteksten en stemuitslagen zijn apart gezet. Voor 2022–2026 zijn de notulen naast de ondertiteling gelegd om bij elke spreekbeurt het moment in de video te vinden. Thema’s zijn vaste lijstjes zoektermen, geen inhoudelijke indeling.</p></div>'+
   '<div><h3>Waar moet je op letten</h3><p>Het knippen en koppelen gaat automatisch en dus soms mis: controleer een citaat in de bron (pdf met paginanummer, of de video) voordat je het gebruikt. Tekst met het label ‘automatische ondertiteling’ is geen officieel verslag en bevat herkenningsfouten. Commissievergaderingen zitten er nog niet in.</p></div>'+
   '</div><p class="by">Gemaakt door <b>Robert Riteco</b>, met hulp van AI. Onofficieel hulpmiddel, geen product van de griffie of de gemeenteraad.</p></section>';
  $('out').innerHTML=h;
}
/* ---------- inzichten ---------- */
let INSP='';
function spark(v){const mx=Math.max(1e-9,...v),W=84,H=22;return '<svg class="spk" viewBox="0 0 '+W+' '+H+'" aria-hidden="true"><polyline points="'+v.map((x,i)=>(2+i*(W-4)/(v.length-1)).toFixed(1)+','+(H-2-(H-4)*x/mx).toFixed(1)).join(' ')+'"/></svg>';}
function renderInsights(){
  const I=META.ins,FL=THEMES.flatMap(g=>g[1]),n1=THEMES[0][1].length,c1=v=>String(Math.round(v)),r1=v=>v.toFixed(1).replace('.',',');
  const cell=(pct,txt,title,data)=>'<td'+(data?' data-ins="'+data+'"':'')+' title="'+esc(title)+'" style="background:color-mix(in srgb,var(--accent) '+Math.round(pct)+'%,transparent);'+(pct>48?'color:var(--accent-ink)':'')+'">'+txt+'</td>';
  const head=k=>k===0||k===n1?'<tr class="grp"><th colspan="99">'+esc(THEMES[k===0?0:1][0])+'</th></tr>':'';
  let h=tabsHTML()+'<p class="hint">Patronen in wat er gezegd is, op basis van de thema’s (vaste lijstjes zoektermen). De getallen zijn treffers per 100.000 gesproken woorden, zodat drukke en rustige jaren en grote en kleine fracties vergelijkbaar zijn. Klik op een cel om de teksten erachter te zien.</p>';
  const yi=y=>I.years.indexOf(y),avg=(row,ys)=>{const v=ys.map(y=>row[yi(y)]).filter(x=>x!=null);return v.reduce((a,b)=>a+b,0)/v.length;};
  const mv=I.names.map((nm,k)=>({k,nm,early:avg(I.ty[k],['2018','2019','2020','2021']),late:avg(I.ty[k],['2025','2026']),n:I.tyn[k].reduce((a,b)=>a+b,0)})).filter(o=>o.n>=100&&o.early>0).map(o=>(o.ch=(o.late-o.early)/o.early,o));
  const up=mv.slice().sort((a,b)=>b.ch-a.ch).slice(0,6),dn=mv.slice().sort((a,b)=>a.ch-b.ch).slice(0,6);
  const mrow=o=>'<button type="button" data-theme="'+esc(FL[o.k][1])+'"><span class="t">'+esc(o.nm)+'</span>'+spark(I.ty[o.k])+'<span class="v '+(o.ch>=0?'up':'dn')+'">'+(o.ch>=0?'+':'−')+Math.abs(Math.round(o.ch*100))+'%</span></button>';
  h+='<div class="charts"><div class="chart"><h3>Stijgers · 2025–2026 vergeleken met 2018–2021</h3><div class="mv">'+up.map(mrow).join('')+'</div></div><div class="chart"><h3>Dalers · 2025–2026 vergeleken met 2018–2021</h3><div class="mv">'+dn.map(mrow).join('')+'</div></div></div>';
  h+='<div class="chart wide"><h3>Wanneer leeft wat · thema per jaar (kleur = aandeel van het piekjaar van dat thema)</h3><div class="hscroll"><table class="heat"><thead><tr><th></th>'+I.years.map(y=>'<th>'+y+'</th>').join('')+'</tr></thead><tbody>'+
    I.names.map((nm,k)=>{const mx=Math.max(1e-9,...I.ty[k]);return head(k)+'<tr><th><a data-theme="'+esc(FL[k][1])+'">'+esc(nm)+'</a></th>'+I.ty[k].map((v,j)=>cell(85*v/mx,c1(v),nm+' · '+I.years[j]+': '+I.tyn[k][j]+' treffers, '+r1(v)+' per 100.000 woorden','y:'+k+':'+I.years[j])).join('')+'</tr>';}).join('')+'</tbody></table></div></div>';
  h+='<div class="chart wide"><h3>Wie heeft het waarover · thema per fractie (raadsleden, alle jaren samen; 1,0× = gemiddelde van de fracties)</h3><div class="hscroll"><table class="heat"><thead><tr><th></th>'+I.parties.map(p=>'<th class="rot"><span>'+esc(p)+'</span></th>').join('')+'</tr></thead><tbody>'+
    I.names.map((nm,k)=>{const row=I.tp[k],mean=row.reduce((a,b)=>a+b,0)/row.length||1e-9;return head(k)+'<tr><th><a data-theme="'+esc(FL[k][1])+'">'+esc(nm)+'</a></th>'+row.map((v,j)=>{const r=v/mean;return I.tpn[k][j]<5?'<td class="lo" title="te weinig treffers">·</td>':cell(r>1?Math.min(85,(r-1)*65):0,'<span'+(r<0.75?' class="lo"':'')+'>'+r1(r)+'×</span>',nm+' · '+I.parties[j]+': '+I.tpn[k][j]+' treffers, '+r1(v)+' per 100.000 woorden','p:'+k+':'+j);}).join('')+'</tr>';}).join('')+'</tbody></table></div></div>';
  const pj=I.parties.indexOf(INSP);
  h+='<div class="chart wide"><h3>Profiel van een fractie</h3><select id="insp" aria-label="Fractie" style="width:auto"><option value="">Kies een fractie…</option>'+I.parties.map(p=>'<option'+(p===INSP?' selected':'')+'>'+esc(p)+'</option>').join('')+'</select>';
  if(pj>=0){const rs=I.names.map((nm,k)=>{const row=I.tp[k],mean=row.reduce((a,b)=>a+b,0)/row.length||1e-9;return {k,nm,r:row[pj]/mean,n:I.tpn[k][pj]};}).filter(o=>o.n>=10).sort((a,b)=>b.r-a.r);
    const li=o=>'<button type="button" data-ins="p:'+o.k+':'+pj+'"><span class="t">'+esc(o.nm)+'</span><span class="b" style="width:'+Math.min(100,Math.round(o.r*40))+'%"></span><span class="v">'+r1(o.r)+'×</span></button>';
    h+='<div class="charts" style="margin:10px 0 0"><div><p class="hint">Hier heeft '+esc(INSP)+' het vaker over dan andere fracties</p><div class="hbars">'+rs.slice(0,6).map(li).join('')+'</div></div><div><p class="hint">En hier minder vaak</p><div class="hbars">'+rs.slice(-6).reverse().map(li).join('')+'</div></div></div>';}
  h+='</div><p class="hint">Lees dit als signaal, niet als meting: een thema is een lijstje woorden, dus een fractie die andere woorden gebruikt voor hetzelfde onderwerp telt minder mee. De fractiecijfers gaan over raadsleden, niet over wethouders.</p>';
  $('out').innerHTML=h;
}
$('out').addEventListener('click',e=>{
  const c=e.target.closest('[data-ins]');
  if(c){const [kind,k,x]=c.dataset.ins.split(':'),FL=THEMES.flatMap(g=>g[1]);for(const f of F)$(f).value=f==='fk'?'01':'';$('q').value=FL[+k][1];
    if(kind==='y'){$('fd1').value=x+'-01-01';$('fd2').value=x+'-12-31';}else{$('fp').value=META.ins.parties[+x];$('fr').value='raad';}
    VIEW='t';update(false);window.scrollTo(0,0);return;}
  const s=e.target.closest('[data-scroll]');if(s){const el=document.getElementById(s.dataset.scroll);if(el)el.scrollIntoView({behavior:'smooth'});return;}
  if(e.target.closest('[data-focus]')){$('q').focus();window.scrollTo(0,0);}
});
$('out').addEventListener('change',e=>{if(e.target.id==='insp'){INSP=e.target.value;renderInsights();}});
