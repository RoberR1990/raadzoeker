// Gedeelde bouwstenen voor de promovideo v4 (stijl van v1): kleuren, animatiehulpjes, kop, kaart, cursor, zoekbalk.
import React from 'react';
import {AbsoluteFill, useCurrentFrame, interpolate, spring, Easing} from 'remotion';

export const C = {groen: '#00811F', groenD: '#004C31', zacht: '#E1EFE2', mid: '#4EB051', grijs: '#EFF4F6', grijs2: '#DBE7EA', lijn: '#CAD6DA', sub: '#3E4B50', navy: '#0E2A4D', blauw: '#00548F', rood: '#D52B1E'};
export const F = 'Arial, Helvetica, sans-serif';
export const FPS = 30;
const ease = Easing.bezier(0.33, 0, 0.2, 1);
export const ci = (f, a, b, c = 0, d = 1, e = ease) => interpolate(f, [a, b], [c, d], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: e});
export const sp = (f, d = 0, cfg = {damping: 16, stiffness: 120}) => spring({frame: f - d, fps: FPS, config: cfg});
export const inSchuif = (f, d, afstand = 40) => ({opacity: ci(f, d, d + 12), transform: `translateY(${ci(f, d, d + 16, afstand, 0)}px)`});
export const nl = (n) => Math.round(n).toLocaleString('nl-NL');

export const Scene = ({dur, children, bg = C.grijs}) => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{background: bg, opacity: Math.min(ci(f, 0, 10), ci(f, dur - 10, dur, 1, 0)), fontFamily: F, color: '#000', overflow: 'hidden'}}>{children}</AbsoluteFill>;
};
export const Kop = ({f, tekst, sub, d = 0, uit = 1e9}) => (
  <div style={{position: 'absolute', left: 90, top: 64, ...inSchuif(f, d, 24), opacity: Math.min(ci(f, d, d + 12), ci(f, uit, uit + 10, 1, 0))}}>
    <div style={{width: ci(f, d + 4, d + 20, 0, 72), height: 8, background: C.groen, borderRadius: 4, marginBottom: 16}} />
    <div style={{fontSize: 60, fontWeight: 700, lineHeight: 1.1}}>{tekst}</div>
    {sub && <div style={{fontSize: 30, color: C.sub, marginTop: 10, opacity: ci(f, d + 10, d + 22)}}>{sub}</div>}
  </div>
);
export const Kaart = ({style, children}) => <div style={{position: 'absolute', background: '#fff', borderRadius: 18, boxShadow: '0 12px 40px rgba(0,40,20,.10)', padding: 36, boxSizing: 'border-box', ...style}}>{children}</div>;
export const Cursor = ({x, y, klik = -99, f}) => {
  const r = ci(f, klik, klik + 14, 0, 60), o = ci(f, klik, klik + 14, 0.5, 0);
  return (
    <div style={{position: 'absolute', left: x, top: y, pointerEvents: 'none', zIndex: 9}}>
      {f >= klik && <div style={{position: 'absolute', left: -r, top: -r, width: 2 * r, height: 2 * r, borderRadius: '50%', background: C.groen, opacity: o}} />}
      <svg width="44" height="54" viewBox="0 0 22 27" style={{position: 'absolute', left: -4, top: -2, transform: `scale(${f >= klik && f < klik + 6 ? 0.85 : 1})`, filter: 'drop-shadow(0 3px 4px rgba(0,0,0,.35))'}}>
        <path d="M2 2 L2 22 L7 17 L11 25 L14.5 23.5 L10.5 15.5 L17.5 15.5 Z" fill="#fff" stroke="#000" strokeWidth="1.6" strokeLinejoin="round" />
      </svg>
    </div>
  );
};
export const Zoekbalk = ({x, y, w, h = 104, tekst = '', caret = true, f = 0}) => (
  <div style={{position: 'absolute', left: x, top: y, width: w, height: h, background: '#fff', borderRadius: h / 2, boxShadow: '0 18px 50px rgba(0,60,30,.16)', border: `2px solid ${C.lijn}`, display: 'flex', alignItems: 'center', paddingLeft: h * 0.42, boxSizing: 'border-box', overflow: 'hidden'}}>
    <svg width={h * 0.36} height={h * 0.36} viewBox="0 0 24 24" style={{flex: 'none'}}><circle cx="10" cy="10" r="7" fill="none" stroke={C.groen} strokeWidth="2.8" /><path d="M15.5 15.5 L22 22" stroke={C.groen} strokeWidth="2.8" strokeLinecap="round" /></svg>
    <div style={{fontSize: h * 0.4, marginLeft: h * 0.24, whiteSpace: 'nowrap', flex: 1, color: tekst ? '#000' : C.sub}}>
      {tekst}{caret && <span style={{display: 'inline-block', width: 3, height: h * 0.42, background: C.groen, marginLeft: 3, verticalAlign: 'middle', opacity: Math.floor(f / 15) % 2 ? 0.1 : 1}} />}
    </div>
    {w > 600 && <div style={{background: C.groen, color: '#fff', fontWeight: 700, fontSize: h * 0.3, borderRadius: 999, padding: `${h * 0.17}px ${h * 0.34}px`, marginRight: h * 0.14, flex: 'none'}}>Zoek</div>}
  </div>
);
// tekst die getypt wordt: aantal letters op frame f
export const getypt = (woord, f, start, perLetter = 3) => woord.slice(0, Math.max(0, Math.floor((f - start) / perLetter)));
// markeer een zoekwoord in een tekst
export const Mark = ({tekst, woord}) => tekst.split(new RegExp(`(${woord})`, 'gi')).map((s, i) => (i % 2 ? <mark key={i} style={{background: C.zacht, color: C.groenD, fontWeight: 700, padding: '0 4px', borderRadius: 4}}>{s}</mark> : s));
// nette zinnen uit een afgekapt fragment: alleen hele zinnen met het zoekwoord
export const zinnen = (t, woord, n = 2) => {
  const z = t.split(/(?<=[.?!])\s+/).slice(1, -1).filter((s) => new RegExp(woord, 'i').test(s));
  if (z.length) return z.slice(0, n).join(' ').trim();
  // geen hele zin met het woord: knip het afgebroken eind weg en het halve woord aan het begin
  const heel = t.split(/(?<=[.?!])\s+/); if (heel.length > 1) heel.pop();
  return heel.join(' ').replace(/^[a-z]\S*\s+/, '').replace(/^\w/, (c) => c.toUpperCase()).trim();
};
