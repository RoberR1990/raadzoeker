/* ---------- toezeggingen ---------- */
let ZT='', TZ=null, MODE='l';
function tzList(s){
  const terms=parseTerms(s.q||s.q2,s.ww),fa=normQ(s.fa),fsn=normQ(s.fs),out=[];
  for(const D of Y){const S=D.s;D.tz.forEach(z=>{const i=z[0],mt=D.M[S.m[i]];
    if((s.fd1&&mt[0]<s.fd1)||(s.fd2&&mt[0]>s.fd2))return;
    if(ZT!==''&&String(z[3])!==ZT)return;
    if(fsn&&!norm(SPK[S.sp[i]][0]).includes(fsn))return;
    if(fa&&!D.In[S.i[i]].includes(fa))return;
    if(terms.length){const lo=Math.max(0,z[1]-400),tx=norm(S.t[i].slice(lo,z[2]+200))+' '+D.In[S.i[i]];if(!terms.some(t=>tx.includes(t.t)))return;}
    out.push({D,z,d:mt[0]});});}
  out.sort((a,b)=>wantSort==='old'?(a.d<b.d?-1:a.d>b.d?1:a.z[0]-b.z[0]):(a.d<b.d?1:a.d>b.d?-1:a.z[0]-b.z[0]));
  return out;
}
function renderToez(s){
  TZ=tzList(s);const terms=parseTerms(s.q||s.q2,s.ww),per={};
  for(const o of TZ){const sp=o.D.s.sp[o.z[0]];per[sp]=(per[sp]||0)+1;}
  const ss=Object.keys(per).map(Number).sort((a,b)=>per[b]-per[a]).slice(0,10),sm=Math.max(1,...ss.map(p=>per[p]));
  let h=tabsHTML()+'<div class="summary"><div class="n"><b>'+nf(TZ.length)+'</b> '+(TZ.length===1?'toezegging':'toezeggingen')+' van collegeleden</div>'+
   '<select id="ztype" aria-label="Soort" style="margin-left:auto"><option value="">Alle soorten</option><option value="0">Uitgesproken toezegging</option><option value="1">Schriftelijk terugkomen / informeren</option></select><button class="btn small" id="csv" type="button">Exporteer (CSV)</button><select id="sort" aria-label="Sortering"><option value="new">Nieuwste eerst</option><option value="old">Oudste eerst</option></select></div>'+
   '<p class="hint">Zinnen waarin een wethouder of de burgemeester iets toezegt (“dat zeg ik toe”, “kan ik toezeggen”) of belooft schriftelijk terug te komen. Automatisch herkend op formulering: dit is geen officiële toezeggingenlijst van de griffie en niet elke toezegging wordt zo uitgesproken. De zoekterm zoekt in de zin, de zinnen ervoor en de titel van het agendapunt; filter op spreker, datum en agendapunt werkt ook.</p>';
  if(ss.length>1)h+='<div class="chart wide"><h3>Per collegelid · klik om te filteren</h3><div class="hbars two">'+ss.map(p=>'<button type="button" data-spk="'+esc(SPK[p][0])+'"><span class="t">'+esc(SPK[p][0])+'</span><span class="b" style="width:'+Math.max(2,Math.round(100*per[p]/sm))+'%"></span><span class="v">'+per[p]+'</span></button>').join('')+'</div></div>';
  if(!TZ.length)h+='<div class="empty">Geen toezeggingen gevonden met deze zoekterm en filters.</div>';
  h+=TZ.slice(0,shown).map((o,k)=>{const D=o.D,i=o.z[0],S=D.s,w=who(D,i),tx=S.t[i].slice(o.z[1],o.z[2]),il=itemLabel(D,S.i[i]);
    return '<article class="card" data-z="'+k+'"><div class="meta"><span class="date">'+fdate(o.d)+'</span><span class="item"><a data-act="zread">'+esc(il.slice(0,170))+(il.length>170?'…':'')+'</a></span></div>'+
     '<div class="who"><b>'+esc(w.name)+'</b>'+(w.party?'<span class="tag party">'+esc(w.party)+'</span>':'')+'<span class="tag">'+w.role+'</span><span class="tag '+(o.z[3]?'':'party')+'">'+(o.z[3]?'schriftelijk terugkomen / informeren':'toezegging')+'</span></div>'+
     '<div class="snip"><p>'+markup(tx,ranges(tx,terms),0,tx.length).replace(/\n/g,' ')+'</p></div>'+
     '<div class="acts"><button class="btn small" data-act="zread" type="button">Debat lezen</button><button class="btn small primary" data-act="zcopy" type="button">Kopieer citaat</button><span class="src">'+vbtn(D,i,'zvideo')+links(D,i).map(l=>'<a href="'+l[1]+'" target="_blank" rel="noopener">'+esc(l[0])+' ↗</a>').join('')+'</span></div></article>';}).join('');
  if(TZ.length>shown)h+='<div class="more-row"><button class="btn primary" id="more" type="button">Toon meer ('+nf(TZ.length-shown)+' resterend)</button></div>';
  $('out').innerHTML=h;$('ztype').value=ZT;$('sort').value=wantSort==='old'?'old':'new';
}
/* ---------- tijdlijn van een dossier ---------- */
function renderTimeline(R){
  const G=new Map();
  for(const o of R.res){const S=o.D.s,m=S.m[o.i],key=o.D.y+':'+m;let g=G.get(key);
    if(!g){g={D:o.D,m,d:o.D.M[m][0],items:new Map(),segs:new Set()};G.set(key,g);}
    const it=S.i[o.i];let x=g.items.get(it);if(!x){x={c:0,n:0,sp:{}};g.items.set(it,x);}
    x.c+=R.q?o.c:1;x.n++;g.segs.add(o.i);const sp=S.sp[o.i];if(sp>=0&&S.ro[o.i]!==1)x.sp[sp]=(x.sp[sp]||0)+1;}
  const gs=[...G.values()].sort((a,b)=>a.d<b.d?-1:1);let h='<div class="tl">',yr='';
  for(const g of gs){const D=g.D,S=D.s;
    if(g.d.slice(0,4)!==yr){yr=g.d.slice(0,4);h+='<div class="ty">'+yr+'</div>';}
    const its=[...g.items.entries()].sort((a,b)=>a[0]-b[0]);
    h+='<div class="tm"><div class="td">'+fdate(g.d)+(D.M[g.m][3]===1?'':'<br><span class="tag warn">geen notulen</span>')+'</div><div class="tb">';
    for(const [it,x] of its){const top=Object.keys(x.sp).map(Number).sort((a,b)=>x.sp[b]-x.sp[a]).slice(0,3).map(p=>SPK[p][0]);
      h+='<div class="ti"><a data-item="'+D.y+':'+it+'">'+esc(itemLabel(D,it).slice(0,160))+'</a><span class="sub">'+(R.q?x.c+(x.c===1?' treffer':' treffers')+' in ':'')+x.n+(x.n===1?' tekst':' teksten')+(top.length?' · '+esc(top.join(', ')):'')+'</span></div>';}
    const strong=new Set(its.filter(e=>e[1].c>=2).map(e=>e[0]));
    (D.moM[g.m]||[]).forEach(k=>{const m=D.mo[k];if(!(R.q&&R.terms.some(t=>D.moN[k].includes(t.t)))&&!(strong.has(S.i[m[0]])&&g.segs.has(m[0])))return;
      h+='<div class="ti mo2"><span class="res '+(m[4]?'ja':'nee')+'">'+(m[4]?'aangenomen':'verworpen')+(m[5]>=0?' '+m[5]+'–'+m[6]:'')+'</span><a data-item="'+D.y+':'+S.i[m[0]]+'">'+MT[m[1]]+(m[2]?' '+esc(m[2]):'')+' · '+esc(m[3].slice(0,140))+'</a></div>';});
    D.tz.forEach(z=>{if(S.m[z[0]]!==g.m||!g.segs.has(z[0]))return;const tx=S.t[z[0]].slice(z[1],z[2]);
      h+='<div class="ti tz2"><span class="tag party">toezegging</span><a data-item="'+D.y+':'+S.i[z[0]]+'"><b>'+esc(SPK[S.sp[z[0]]][0])+':</b> '+esc(tx.slice(0,220))+(tx.length>220?'…':'')+'</a></div>';});
    h+='</div></div>';}
  return h+'</div>';
}
function riseHTML(){
  const I=META.ins;if(!I.rise)return '';
  return '<div class="chart wide"><h3>Opkomende woorden · vallen in 2025–2026 veel vaker dan in 2018–2022</h3><div class="rise">'+I.rise.map(r=>'<button type="button" data-theme="&quot;'+esc(r[0])+'&quot;" title="'+r[1]+'× in 2025–2026, '+r[2]+'× in 2018–2022"><span class="t">'+esc(r[0])+'</span>'+spark(r[3])+'<span class="v">'+r[1]+'×</span></button>').join('')+'</div><p class="hint" style="margin:8px 0 0">Zonder vooraf bedachte thema’s: alle woorden uit de notulen zijn geteld. Namen van sprekers en vergadertaal zijn weggelaten.</p></div>';
}
function collHTML(){
  const I=META.ins;if(!I.coll)return '';const FL=THEMES.flatMap(g=>g[1]),n1=THEMES[0][1].length,r1=v=>v.toFixed(1).replace('.',',');
  return '<div class="chart wide"><h3>College · thema per wethouder of burgemeester (1,0× = gemiddelde van deze collegeleden)</h3><div class="hscroll"><table class="heat"><thead><tr><th></th>'+I.coll.map(p=>'<th class="rot"><span>'+esc(p)+'</span></th>').join('')+'</tr></thead><tbody>'+
    I.names.map((nm,k)=>{const row=I.tw[k],mean=row.reduce((a,b)=>a+b,0)/row.length||1e-9;return (k===0||k===n1?'<tr class="grp"><th colspan="99">'+esc(THEMES[k===0?0:1][0])+'</th></tr>':'')+'<tr><th><a data-theme="'+esc(FL[k][1])+'">'+esc(nm)+'</a></th>'+row.map((v,j)=>{const r=v/mean,pct=r>1?Math.min(85,(r-1)*40):0;return I.twn[k][j]<5?'<td class="lo" title="te weinig treffers">·</td>':'<td data-ins="w:'+k+':'+j+'" title="'+esc(nm+' · '+I.coll[j]+': '+I.twn[k][j]+' treffers, '+r1(v)+' per 100.000 woorden')+'" style="background:color-mix(in srgb,var(--accent) '+Math.round(pct)+'%,transparent);'+(pct>48?'color:var(--accent-ink)':'')+'"><span'+(r<0.75?' class="lo"':'')+'>'+r1(r)+'×</span></td>';}).join('')+'</tr>';}).join('')+'</tbody></table></div><p class="hint" style="margin:8px 0 0">Laat vooral de portefeuilles zien: een wethouder praat het meest over het eigen dossier. Alleen wat zij zeiden als collegelid, niet als voorzitter.</p></div>';
}
