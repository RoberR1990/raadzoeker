/* Eén telregel voor dossierpagina, briefing en deelkaart (Python: src/deelkaart.py tel()).
   Bron: d/<slug>.json (moties en toezeggingen uit iBabs, sinds 2018). Bestaat er een d/<slug>-extra.json, dan telt het beloftespoor
   daaruit (ingediend sinds 2022; X.tel.aan = aangenomen moties sinds 2022). Over de termijn = laatste stap 'verwacht' met een datum voor de stand. */
function telling(d,X,stand){
  stand=stand||STAND;
  if(X&&X.spoor){
    const op=X.spoor.filter(x=>x.open),laat=x=>{const l=(x.stappen||[]).slice(-1)[0];return !!l&&l[1]==='verwacht'&&l[0]<stand;};
    const mo=op.filter(x=>x.soort==='motie'),tz=op.filter(x=>x.soort==='toezegging');
    const aan=X.tel?X.tel.aan:X.spoor.filter(x=>x.soort==='motie').length;
    return {sinds:'2022',aan,af:Math.max(0,aan-mo.length),mo:mo.length,mo_laat:mo.filter(laat).length,tz:tz.length,tz_laat:tz.filter(laat).length};
  }
  return {sinds:'2018',aan:d.moties.aangenomen,af:d.moties.afgedaan,mo:d.moties.open,mo_laat:d.moties.te_laat,tz:d.toez.open,tz_laat:d.toez.te_laat};
}
/* de vier cijfers (label, getal, onderregel) die overal hetzelfde heten */
function telCijfers(t){
  const laat=n=>n?`<span class="stip laat"></span>waarvan ${n} over de termijn`:'geen over de termijn';
  return [['moties aangenomen',t.aan,`sinds ${t.sinds} · ${nf(t.af)} afgedaan`],['moties in uitvoering',t.mo,laat(t.mo_laat)+(t.sinds==='2022'?' · sinds 2022':'')],['toezeggingen open',t.tz,laat(t.tz_laat)+(t.sinds==='2022'?' · sinds 2022':'')]];
}
/* alleen een samenvatting tonen die over dit onderwerp zelf gaat (eigen thema), niet over het bredere thema */
function eigenTsum(d){
  const ts=d.tsum;if(!ts)return null;
  if((d.soort==='onderwerp'||d.soort==='thema')&&d.tsum_thema&&d.tsum_thema!==d.naam)return null;
  return ts;
}
const GEEN_SAMEN='Voor dit onderwerp is nog geen samenvatting gemaakt.';
