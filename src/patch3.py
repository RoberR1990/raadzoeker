t=open('template.html').read()
def rep(old,new,all=False):
    global t
    assert old in t,old[:70]
    t=t.replace(old,new) if all else t.replace(old,new,1)
# --- THEMES from meta
a=t.index("const THEMES=["); b=t.index("const PALIAS=")
t=t[:a]+"""const THEMES=META.themes, TSTR={};
THEMES.forEach(g=>g[1].forEach(th=>{TSTR[th[1]]={th,sub:-1};th[2].forEach((s,k)=>{TSTR[s[1]]={th,sub:k};});}));
"""+t[b:]
# --- header logo
rep('<h1>Raad<span>zoeker</span></h1>','<h1><a id="home" href="#" title="Naar de startpagina">Raad<span>zoeker</span></a></h1>')
# --- tabs
rep("""<button type="button" role="tab" data-view="m" class="'+(VIEW==='m'?'on':'')+'">Moties &amp; stemmingen</button></div>';}""",
    """<button type="button" role="tab" data-view="m" class="'+(VIEW==='m'?'on':'')+'">Moties &amp; stemmingen</button><button type="button" role="tab" data-view="i" class="'+(VIEW==='i'?'on':'')+'">Inzichten</button></div>';}""")
rep("VIEW=p.get('v')==='m'?'m':'t';","VIEW=['m','i'].includes(p.get('v'))?p.get('v'):'t';")
rep("if(VIEW==='m'){RES=null;renderMotions(s);return;}","if(VIEW==='m'){RES=null;renderMotions(s);return;}\n  if(VIEW==='i'){RES=null;renderInsights();return;}")
# --- links / video buttons
a=t.index("function links(D,i){"); b=t.index("function itemLabel(D,it)")
t=t[:a]+"""function links(D,i){
  const S=D.s,m=D.M[S.m[i]],o=[];
  if(m[1])o.push(['Vergadering (iBabs)',SRC+'/Agenda/Index/'+m[1]]);
  if(S.d[i]>=0){const d=D.D[S.d[i]];o.push(['Notulen (pdf)'+(S.pg[i]?' · p. '+S.pg[i]:''),SRC+'/Agenda/Document/'+d[1]+'?documentId='+d[0]+(d[2]?'&agendaItemId='+d[2]:'')]);}
  return o;
}
function vbtn(D,i,act){const S=D.s;return S.v[i]>=0&&D.M[S.m[i]][4]?'<button type="button" class="vb" data-act="'+act+'" title="Speel de uitzending af vanaf dit moment">▶ video '+hms(S.v[i])+'</button>':'';}
"""+t[b:]
rep("""h+='<span class="src">'+links(D,i).map(""","""h+='<span class="src">'+vbtn(D,i,'video')+links(D,i).map(""")
rep("""(S.v[i]>=0?(k!==4&&S.pg[i]?' · ':'')+'▶ '+hms(S.v[i]):'')+'</span>""","""'</span>'+vbtn(D,i,'rvideo')+'""")
rep("""  else if(t.dataset.act==='copy')copy(citation(o.D,o.i,selIn(card.querySelector('.snip'))));""","""  else if(t.dataset.act==='copy')copy(citation(o.D,o.i,selIn(card.querySelector('.snip'))));
  else if(t.dataset.act==='video')openVideo(o.D,o.i);""")
rep("""$('rbody').addEventListener('click',e=>{const t=e.target.closest('[data-act="rcopy"]');if(!t||!RD)return;const sp=t.closest('.sp');copy(citation(RD.D,+sp.dataset.i,selIn(sp)));});""",
"""$('rbody').addEventListener('click',e=>{const t=e.target.closest('[data-act]');if(!t||!RD)return;const sp=t.closest('.sp');if(t.dataset.act==='rvideo')openVideo(RD.D,+sp.dataset.i);else if(t.dataset.act==='rcopy')copy(citation(RD.D,+sp.dataset.i,selIn(sp)));});
/* ---------- video: ingebouwde speler die naar het moment springt ---------- */
let VP=null;
function openVideo(D,i){
  const S=D.s,m=D.M[S.m[i]],ref=m[4],sec=Math.max(0,S.v[i]-3),box=$('vbox');closeVideo();
  $('vtitle').textContent=fdate(m[0])+' · '+who(D,i).name;$('vjump').textContent='Spring naar '+hms(sec);
  $('vlink').href=m[1]?SRC+'/Agenda/Index/'+m[1]:'#';$('vnote').textContent='Klik in de speler op Start; de uitzending begint dan op '+hms(sec)+'. Staat hij ergens anders, klik dan op ‘Spring naar’. De tijd is bij benadering.';
  $('video').classList.add('on');
  const fail=()=>{box.innerHTML='<div class="empty">De speler kon niet worden geladen (geen internet, of de speler wordt hier geblokkeerd). Open de vergadering in iBabs en spoel naar '+hms(sec)+'.</div>';};
  if(ref.startsWith('c:')){
    const go=()=>{try{const p=cwc.sdk.player.client.createPlayer({id:ref.slice(2),display:126});p.element.style.cssText='width:100%;height:100%;border:0';p.element.setAttribute('allow','fullscreen; autoplay');box.appendChild(p.element);
      const jump=()=>{try{p.seek({timestamp:sec*1000});}catch(e){}};VP={jump,stop:()=>{try{p.destroy();}catch(e){}}};try{p.on('ready',jump);}catch(e){}setTimeout(jump,2500);setTimeout(jump,6000);}catch(e){fail();}};
    if(window.cwc&&cwc.sdk)go();else{const sc=document.createElement('script');sc.src='https://sdk.companywebcast.com/sdk/player/client.js';sc.onload=go;sc.onerror=fail;document.head.appendChild(sc);}
  }else{
    const f=document.createElement('iframe');f.allow='fullscreen; autoplay';f.style.cssText='width:100%;height:100%;border:0';f.src='https://connectlive.ibabs.eu/Player/Player/'+ref.slice(2);box.appendChild(f);
    const jump=()=>{try{f.contentWindow.postMessage({action:'jumpToPosition',seconds:sec},'https://connectlive.ibabs.eu/');}catch(e){}};VP={jump,stop:()=>{}};f.onload=()=>{setTimeout(jump,2500);setTimeout(jump,6000);};
  }
}
function closeVideo(){if(VP){VP.stop();VP=null;}$('vbox').innerHTML='';$('video').classList.remove('on');}
$('vjump').addEventListener('click',()=>VP&&VP.jump());
$('vclose').addEventListener('click',closeVideo);
$('video').addEventListener('click',e=>{if(e.target.id==='video')closeVideo();});
$('home').addEventListener('click',e=>{e.preventDefault();for(const f of F)$(f).value=f==='fk'?'01':'';$('ww').checked=false;wantSort='new';MRES='';VIEW='t';update(false);window.scrollTo(0,0);});""")
rep("if(e.key==='Escape'&&RD)closeReader();","if(e.key==='Escape'){if($('video').classList.contains('on'))closeVideo();else if(RD)closeReader();}")
rep('<div id="toast" role="status"></div>','''<div id="video" role="dialog" aria-modal="true" aria-label="Video"><div class="vp">
  <header><b id="vtitle"></b><button class="btn small primary" id="vjump" type="button"></button><a id="vlink" class="sub" target="_blank" rel="noopener">Open in iBabs ↗</a><button class="btn small" id="vclose" type="button" style="margin-left:auto">Sluiten ✕</button></header>
  <div id="vbox"></div><p class="sub" id="vnote"></p></div></div>
<div id="toast" role="status"></div>''')
# citation unchanged; zoom bar + home + insights
rep("  let h=tabsHTML()+'<div class=\"summary\"><div class=\"n\"><b>'+nf(res.length)+'</b> '+(res.length===1?'tekst':'teksten')","  let h=tabsHTML()+zoomHTML()+'<div class=\"summary\"><div class=\"n\"><b>'+nf(res.length)+'</b> '+(res.length===1?'tekst':'teksten')")
a=t.index("function renderBrowse(){"); b=t.index("function fillMeeting(el){")
home=open('home.js').read()
t=t[:a]+home+t[b:]
rep("$('theme').insertAdjacentHTML('beforeend',THEMES.map(g=>'<optgroup label=\"'+esc(g[0])+'\">'+g[1].map(t=>'<option value=\"'+esc(t[1])+'\">'+esc(t[0])+'</option>').join('')+'</optgroup>').join(''));",
    "$('theme').insertAdjacentHTML('beforeend',THEMES.map(g=>'<optgroup label=\"'+esc(g[0])+'\">'+g[1].map(t=>'<option value=\"'+esc(t[1])+'\">'+esc(t[0])+'</option>').join('')+'</optgroup>').join(''));")
# footer
a=t.index('<div class="wrap"><footer>'); b=t.index('</footer></div>')+len('</footer></div>')
t=t[:a]+'<div class="wrap"><footer>Raadzoeker · gemaakt door Robert Riteco · onofficieel hulpmiddel, geen product van de griffie · bron: <a href="https://gemeenteraad.rotterdam.nl" target="_blank" rel="noopener">gemeenteraad.rotterdam.nl</a> · stand <span id="built"></span> · <a href="#" id="about">Over deze tool en de data</a></footer></div>'+t[b:]
rep("$('rclose').addEventListener('click',closeReader);","$('rclose').addEventListener('click',closeReader);\n$('about').addEventListener('click',e=>{e.preventDefault();$('home').click();setTimeout(()=>{const a=document.getElementById('over');if(a)a.scrollIntoView();},50);});")
assert t.count('</style>')==1
t=t.replace('</style>',open('extra2.css').read().rstrip())
open('template.html','w').write(t)
print('patched')
