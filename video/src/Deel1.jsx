// Promovideo v4, deel 1 (0–24 s): woordwolk -> logo, daarna Vergaderingen met echte schermen van de site.
// Schermen: public/shots/*.png (python video/opname.py deel1, 3840x2160 = 2x), plekken van knoppen in shots.json (css-px op 1920x1080).
import React from 'react';
import {AbsoluteFill, Sequence, Img, staticFile, useCurrentFrame, interpolate, spring, Easing} from 'remotion';
import D from './data.json';
import P from '../public/shots/shots.json';

const C = {groen: '#00811F', groenD: '#004C31', zacht: '#E1EFE2', grijs: '#EFF4F6', sub: '#3E4B50', navy: '#0E2A4D'};
const F = 'Arial, Helvetica, sans-serif';
const FPS = 30;
export const DUUR1 = 720;
const ease = Easing.bezier(0.33, 0, 0.2, 1);
const ci = (f, a, b, c = 0, d = 1, e = ease) => interpolate(f, [a, b], [c, d], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: e});
const sp = (f, d = 0, cfg = {damping: 16, stiffness: 120}) => spring({frame: f - d, fps: FPS, config: cfg});
const mid = (b) => [b[0] + b[2] / 2, b[1] + b[3] / 2];

// tekst in beeld: kaartje linksonder met groen streepje
const Titel = ({f, tekst, d = 8}) => (
  <div style={{position: 'absolute', left: 70, bottom: 70, opacity: ci(f, d, d + 12), transform: `translateY(${ci(f, d, d + 14, 30, 0)}px)`,
    background: '#fff', borderRadius: 18, padding: '22px 34px 24px', boxShadow: '0 18px 50px rgba(0,40,20,.22)', fontFamily: F}}>
    <div style={{width: ci(f, d + 4, d + 20, 0, 70), height: 8, background: C.groen, borderRadius: 4, marginBottom: 12}} />
    <div style={{fontSize: 56, fontWeight: 700, lineHeight: 1.1, color: '#000'}}>{tekst}</div>
  </div>
);
const Cursor = ({x, y, klik = -99, f}) => {
  const r = ci(f, klik, klik + 14, 0, 60), o = ci(f, klik, klik + 14, 0.5, 0);
  return (
    <div style={{position: 'absolute', left: x, top: y, pointerEvents: 'none'}}>
      {f >= klik && <div style={{position: 'absolute', left: -r, top: -r, width: 2 * r, height: 2 * r, borderRadius: '50%', background: C.groen, opacity: o}} />}
      <svg width="44" height="54" viewBox="0 0 22 27" style={{position: 'absolute', left: -4, top: -2, transform: `scale(${f >= klik && f < klik + 6 ? 0.85 : 1})`, filter: 'drop-shadow(0 3px 4px rgba(0,0,0,.35))'}}>
        <path d="M2 2 L2 22 L7 17 L11 25 L14.5 23.5 L10.5 15.5 L17.5 15.5 Z" fill="#fff" stroke="#000" strokeWidth="1.6" strokeLinejoin="round" />
      </svg>
    </div>
  );
};
// schermafbeelding met camera: zoom s rond punt (cx,cy) in css-px; cursor en effecten bewegen mee via toScherm
const Scherm = ({src, s = 1, cx = 960, cy = 540, o = 1, children}) => {
  // camera blijft binnen de schermafbeelding (geen lege randen)
  cx = Math.min(Math.max(cx, 960 / s), 1920 - 960 / s); cy = Math.min(Math.max(cy, 540 / s), 1080 - 540 / s);
  return (
  <AbsoluteFill style={{opacity: o, overflow: 'hidden', background: C.grijs}}>
    <div style={{position: 'absolute', left: 0, top: 0, width: 1920, height: 1080, transformOrigin: '0 0',
      transform: `translate(${960 - cx * s}px, ${540 - cy * s}px) scale(${s})`}}>
      <Img src={staticFile('shots/' + src)} style={{width: 1920, height: 1080}} />
      {children}
    </div>
  </AbsoluteFill>
);};
const Fade = ({dur, children}) => {const f = useCurrentFrame(); return <AbsoluteFill style={{opacity: Math.min(ci(f, 0, 8), ci(f, dur - 8, dur, 1, 0))}}>{children}</AbsoluteFill>;};

/* 0–4 s: woordenwolk trekt samen tot het logo */
const WOLK = (() => {
  const max = D.wolk[0][1], uit = [], vak = [];
  D.wolk.forEach(([w, g], i) => {
    const fs = Math.round(26 + 62 * Math.sqrt(g / max)), bw = w.length * fs * 0.54 + 24, bh = fs * 1.25;
    for (let t = 0; t < 4000; t += 1) {
      const a = t * 0.17, r = 4 * t ** 0.62, cx = 960 + r * Math.cos(a) * 1.7, cy = 540 + r * Math.sin(a);
      const b = [cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2];
      if (b[0] < 40 || b[2] > 1880 || b[1] < 40 || b[3] > 1040) continue;
      if (vak.some((v) => !(b[2] < v[0] || b[0] > v[2] || b[3] < v[1] || b[1] > v[3]))) continue;
      vak.push(b); uit.push({w, fs, x: cx, y: cy, i}); break;
    }
  });
  return uit;
})();
const KLEUR = [C.groen, C.navy, '#000', C.sub, C.groen, C.navy];
const Intro = () => {
  const f = useCurrentFrame();
  const lg = sp(f, 62, {damping: 13, stiffness: 110});
  return (
    <AbsoluteFill style={{background: C.grijs, fontFamily: F, opacity: ci(f, 112, 120, 1, 0)}}>
      {WOLK.map(({w, fs, x, y, i}) => {
        const s = sp(f, i * 0.7, {damping: 14, stiffness: 140}), m = ci(f, 40 + (i % 9), 70 + (i % 9), 0, 1, Easing.in(Easing.cubic));
        return <div key={w} style={{position: 'absolute', left: x + (960 - x) * m, top: y + (470 - y) * m, transform: `translate(-50%,-50%) scale(${s * (1 - 0.8 * m)})`,
          opacity: Math.min(s, 1 - m), fontSize: fs, fontWeight: i < 10 ? 700 : 400, color: KLEUR[i % 6], whiteSpace: 'nowrap'}}>{w}</div>;
      })}
      <div style={{position: 'absolute', left: 960, top: 470, transform: `translate(-50%,-50%) scale(${lg})`, opacity: Math.min(1, lg)}}>
        <Img src={staticFile('logo.svg')} style={{width: 340}} />
      </div>
      <div style={{position: 'absolute', left: 0, right: 0, top: 640, textAlign: 'center', fontSize: 92, fontWeight: 700, color: C.navy, opacity: ci(f, 74, 88), transform: `translateY(${ci(f, 74, 90, 20, 0)}px)`}}>raadzoeker</div>
      <div style={{position: 'absolute', left: 0, right: 0, top: 752, textAlign: 'center', fontSize: 36, color: C.sub, opacity: ci(f, 84, 98)}}>wat de Rotterdamse raad zegt, besluit en belooft</div>
    </AbsoluteFill>
  );
};

/* 4–8 s: overzicht Vergaderingen, klik op 'Lees in 1 minuut' */
const Overzicht = () => {
  const f = useCurrentFrame(), k = mid(P.d1_overzicht.hero);
  const s = ci(f, 0, 120, 1.0, 1.12), x = ci(f, 30, 85, 1500, k[0]), y = ci(f, 30, 85, 900, k[1]);
  return (<Fade dur={120}><Scherm src="d1_overzicht.png" s={s} cx={ci(f, 0, 120, 960, 800)} cy={ci(f, 0, 120, 540, 480)}><Cursor x={x} y={y} klik={92} f={f} /></Scherm><Titel f={f} tekst="Elke vergadering samengevat" /></Fade>);
};
/* 8–13 s: samenvatting in één minuut */
const Kort = () => {
  const f = useCurrentFrame();
  return (<Fade dur={150}><Scherm src="d1_kort.png" s={ci(f, 0, 150, 1.18, 1.3)} cx={760} cy={ci(f, 0, 150, 470, 560)} /><Titel f={f} tekst="Lees het in één minuut" /></Fade>);
};
/* 13–19 s: tik op een fractie -> citaat -> moment in de video */
const Fractie = () => {
  const f = useCurrentFrame(), pt = P.d1_fracties.pt, sp1 = P.d1_citaat.speel;
  const ptx = pt[0] + 60, pty = pt[1] + pt[3] / 2, k = mid(sp1);
  const s = ci(f, 0, 110, 1.25, 1.5);
  return (
    <Fade dur={180}>
      {f < 52 && <Scherm src="d1_fracties.png" s={s} cx={1080} cy={300}><Cursor x={ci(f, 4, 34, 1300, ptx)} y={ci(f, 4, 34, 700, pty)} klik={40} f={f} /></Scherm>}
      {f >= 48 && f < 116 && <Scherm src="d1_citaat.png" s={s} cx={1080} cy={300} o={ci(f, 48, 56)}><Cursor x={ci(f, 58, 90, ptx, k[0])} y={ci(f, 58, 90, pty, k[1])} klik={96} f={f} /></Scherm>}
      {f >= 110 && <AbsoluteFill style={{opacity: ci(f, 110, 122), background: '#111'}}>
        <Img src={staticFile('shots/d1_video.jpg')} style={{position: 'absolute', left: '50%', top: '50%', width: 1920 * ci(f, 110, 180, 1.32, 1.42), transform: 'translate(-50%,-46%)'}} />
      </AbsoluteFill>}
      <Titel f={f} tekst="Wie zei wat, letterlijk" />
    </Fade>
  );
};
/* 19–24 s: moties met uitslag */
const Moties = () => {
  const f = useCurrentFrame(), mo = P.d1_moties.mo;
  return (<Fade dur={150}><Scherm src="d1_moties.png" s={ci(f, 0, 150, 1.25, 1.42)} cx={1000} cy={ci(f, 0, 150, mo[1] - 40, mo[1] + 60)} /><Titel f={f} tekst="Van commissie tot besluit" /></Fade>);
};

export const Deel1 = () => (
  <AbsoluteFill style={{background: C.grijs}}>
    <Sequence from={0} durationInFrames={120}><Intro /></Sequence>
    <Sequence from={120} durationInFrames={120}><Overzicht /></Sequence>
    <Sequence from={240} durationInFrames={150}><Kort /></Sequence>
    <Sequence from={390} durationInFrames={180}><Fractie /></Sequence>
    <Sequence from={570} durationInFrames={150}><Moties /></Sequence>
  </AbsoluteFill>
);
