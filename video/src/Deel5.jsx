// Promovideo v4, deel 5 (13 s): slot. Logo, de vier kernpunten (vergaderingen, zoeken, pagina's, volgen), dan raadzoeker.nl.
import React from 'react';
import {AbsoluteFill, Img, staticFile, useCurrentFrame} from 'remotion';
import {C, F, ci, sp, inSchuif} from './stijl';

export const DUUR5 = 390;
const I = {
  verg: <><rect x="6" y="10" width="36" height="30" rx="4" fill="none" stroke="#fff" strokeWidth="3.4" /><path d="M6 18 H42 M15 6 V13 M33 6 V13" stroke="#fff" strokeWidth="3.4" strokeLinecap="round" /><path d="M13 26 H35 M13 33 H27" stroke="#fff" strokeWidth="3" strokeLinecap="round" /></>,
  zoek: <><circle cx="20" cy="20" r="12" fill="none" stroke="#fff" strokeWidth="3.6" /><path d="M29 29 L41 41" stroke="#fff" strokeWidth="4" strokeLinecap="round" /></>,
  pag: <><rect x="8" y="6" width="26" height="34" rx="3" fill="none" stroke="#fff" strokeWidth="3.4" /><rect x="15" y="11" width="26" height="34" rx="3" fill={C.groen} stroke="#fff" strokeWidth="3.4" /><path d="M21 21 H35 M21 28 H35 M21 35 H30" stroke="#fff" strokeWidth="3" strokeLinecap="round" /></>,
  volg: <path d="M24 5 L29.5 17.5 L43 18.8 L32.8 27.8 L35.8 41 L24 34 L12.2 41 L15.2 27.8 L5 18.8 L18.5 17.5 Z" fill="none" stroke="#fff" strokeWidth="3.4" strokeLinejoin="round" />,
};
const PUNT = [
  ['verg', 'Elke vergadering samengevat', 'in 1 minuut of 10 minuten, met video'],
  ['zoek', 'Zoek in alles', 'wat de raad sinds 2018 zei en schreef'],
  ['pag', 'Een pagina per domein, onderwerp en gebied', 'gezegd, besloten en beloofd'],
  ['volg', 'Volg ieder onderwerp', 'en krijg een seintje bij nieuws'],
];

export const Deel5 = () => {
  const f = useCurrentFrame(), eind = 250;
  const logo = sp(f, 0, {damping: 14, stiffness: 90}), naarBoven = ci(f, 50, 80);
  return (
    <AbsoluteFill style={{background: C.grijs, fontFamily: F, overflow: 'hidden', opacity: ci(f, 0, 10)}}>
      {/* logo groot, schuift daarna naar boven */}
      <div style={{position: 'absolute', left: 0, right: 0, top: 330 - 230 * naarBoven, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 30,
        transform: `scale(${(0.7 + 0.3 * logo) * (1 - 0.35 * naarBoven)})`, opacity: Math.min(ci(f, 0, 14), ci(f, eind - 10, eind, 1, 0))}}>
        <Img src={staticFile('logo.svg')} style={{width: 300}} />
        <div style={{fontSize: 130, fontWeight: 700, color: C.groenD}}>raadzoeker</div>
      </div>
      {/* vier kernpunten */}
      {PUNT.map(([ic, kop, sub], i) => {
        const d = 80 + i * 32, s = sp(f, d, {damping: 15, stiffness: 120});
        return (
          <div key={ic} style={{position: 'absolute', left: 260, top: 380 + i * 150, display: 'flex', alignItems: 'center', gap: 36,
            opacity: Math.min(ci(f, d, d + 10), ci(f, eind - 10, eind, 1, 0)), transform: `translateX(${(1 - s) * -80}px)`}}>
            <div style={{width: 110, height: 110, borderRadius: 28, background: C.groen, display: 'flex', alignItems: 'center', justifyContent: 'center', flex: 'none',
              transform: `scale(${0.6 + 0.4 * s})`}}>
              <svg width="64" height="64" viewBox="0 0 48 48">{I[ic]}</svg>
            </div>
            <div>
              <div style={{fontSize: 56, fontWeight: 700, lineHeight: 1.1}}>{kop}</div>
              <div style={{fontSize: 32, color: C.sub, marginTop: 6}}>{sub}</div>
            </div>
          </div>
        );
      })}
      {/* eindbeeld: adres */}
      <AbsoluteFill style={{background: C.groen, opacity: ci(f, eind - 6, eind + 8), alignItems: 'center', justifyContent: 'center', color: '#fff'}}>
        <div style={{display: 'flex', alignItems: 'center', gap: 28, ...inSchuif(f, eind + 4, 30)}}>
          <Img src={staticFile('logo-wit.svg')} style={{width: 150}} />
          <div style={{fontSize: 150, fontWeight: 700}}>raadzoeker.nl</div>
        </div>
        <div style={{fontSize: 38, marginTop: 40, ...inSchuif(f, eind + 26, 20)}}>Open voor iedereen · elke paar uur bijgewerkt</div>
        <div style={{fontSize: 32, marginTop: 18, opacity: 0.9, ...inSchuif(f, eind + 40, 20)}}>Vragen? RIO-groep Raadzoeker</div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
