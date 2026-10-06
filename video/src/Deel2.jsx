// Promovideo v4, deel 2 (16 s): Zoeken. Diepte (één woord, alle soorten bronnen) en breedte (snel wisselende woorden).
// Echte resultaten uit de zoekfunctie van de site (src/d2.json, src/d2b_ruw.json).
import React from 'react';
import {AbsoluteFill, Sequence, useCurrentFrame} from 'remotion';
import {C, F, ci, sp, inSchuif, Scene, Kop, Kaart, Zoekbalk, getypt, Mark} from './stijl';
import X from './d2.json';
import B from './d2b_ruw.json';

export const DUUR2 = 510;
const W = X.woonfraude;
const getal = (s, f, a, b) => Math.round(+String(s).replace(/\./g, '') * ci(f, a, b)).toLocaleString('nl-NL');

// zes soorten bronnen bij 'woonfraude' (titels en data uit de zoekresultaten)
const BRON = [
  ['Vergaderverslag', C.groen, W.verslag[0][1], 'Gemeenteraad · 1 okt 2026', 'Het debat over malafide verhuurders en handhaving, samengevat'],
  ['Debat', C.navy, 'Rashied Dahoe (DENK)', 'Commissie · 3 jul 2025', '‘De aanpak op woonfraude moet niet alleen gericht zijn op statushouders.’'],
  ['Motie', '#8A5A00', 'Niet frauderen op Zuid', 'Leefbaar Rotterdam · 11 apr 2019', 'Het onderwerp woonfraude heeft recent veel aandacht'],
  ['Vragen en antwoord', C.blauw, 'Onderverhuur sociale huur: wat gebeurt er echt?', 'Leefbaar Rotterdam · 8 jan 2026 · beantwoord 14 apr', 'Wat doet de gemeente concreet tegen illegale onderhuur en woonfraude?'],
  ['Collegebrief', C.sub, 'Voortgang Goed Huren en Verhuren 2025', 'College · 12 feb 2026', 'Samen optrekken tegen overbewoning, woonfraude en onderhoudsproblemen'],
  ['Wijkraad', C.mid, 'Uitvoeringsplan Integrale Aanpak Tarwewijk', 'Wijkraad Tarwewijk · 24 mrt 2026', 'Aanpak van woonoverlast, woonfraude, te hoge huren'],
];
const BREED = ['tramlijn 4', 'Tweebosbuurt', 'hittestress', 'deelscooters', 'Feyenoord'];

const Diepte = () => {
  const f = useCurrentFrame();
  return (
    <Scene dur={300}>
      <Kop f={f} tekst="Zoek in alles wat de raad zei en schreef" sub="Debatten, verslagen, moties, vragen, brieven en wijkraden, sinds 2018" />
      <Zoekbalk x={90} y={250} w={1000} h={88} tekst={getypt('woonfraude', f, 22)} f={f} />
      <div style={{position: 'absolute', left: 1130, top: 264, display: 'flex', gap: 14, ...inSchuif(f, 58, 14)}}>
        <div style={{fontSize: 28, fontWeight: 700, background: C.groen, color: '#fff', borderRadius: 999, padding: '12px 26px'}}>Gezegd <span style={{fontWeight: 400}}>{getal(W.ng, f, 58, 84)}</span></div>
        <div style={{fontSize: 28, fontWeight: 700, background: '#fff', borderRadius: 999, padding: '12px 26px'}}>Stukken <span style={{fontWeight: 400}}>{getal(W.ns, f, 58, 84)}</span></div>
      </div>
      {BRON.map(([soort, kl, titel, waar, tekst], i) => {
        const d = 76 + i * 16, s = sp(f, d, {damping: 15, stiffness: 120}), col = i % 3, rij = Math.floor(i / 3);
        return (
          <Kaart key={soort} style={{left: 90 + col * 590, top: 380 + rij * 330, width: 560, height: 300, padding: '26px 30px', borderTop: `7px solid ${kl}`,
            opacity: Math.min(1, s), transform: `translateY(${(1 - s) * 60}px) scale(${0.94 + 0.06 * s})`}}>
            <span style={{fontSize: 20, fontWeight: 700, color: '#fff', background: kl, borderRadius: 999, padding: '4px 14px'}}>{soort}</span>
            <div style={{fontSize: 30, fontWeight: 700, lineHeight: 1.2, margin: '16px 0 6px'}}>{titel}</div>
            <div style={{fontSize: 20, color: C.sub}}>{waar}</div>
            <div style={{fontSize: 24, lineHeight: 1.4, marginTop: 12}}><Mark tekst={tekst} woord="woonfraude" /></div>
          </Kaart>
        );
      })}
    </Scene>
  );
};

// kleine rood-witte knipoog bij Feyenoord, rond de zoekbalk
const Knipoog = ({f, start}) => f < start ? null : (
  <>{Array.from({length: 26}, (_, i) => {const t = f - start, a = (i / 26) * Math.PI * 2, r = t * (7 + (i % 5));
    return <div key={i} style={{position: 'absolute', left: 960 + Math.cos(a) * r * 1.6, top: 470 + Math.sin(a) * r * 0.7 + t * t * 0.08, width: 14, height: 7, background: i % 2 ? C.rood : '#fff', border: i % 2 ? 'none' : `1px solid ${C.lijn}`, transform: `rotate(${t * 12 + i * 30}deg)`, opacity: ci(f, start + 33, start + 49, 1, 0)}} />;})}</>
);
const Breedte = () => {
  const f = useCurrentFrame(), per = 34, i = Math.min(BREED.length - 1, Math.floor(Math.max(0, f - 14) / per)), q = BREED[i], t0 = 14 + i * per;
  const [ng, ns] = B.breed[q];
  return (
    <Scene dur={210}>
      <Kop f={f} tekst="Over elk onderwerp" sub="Van tramlijn tot Tweebosbuurt" />
      <Zoekbalk x={380} y={420} w={1160} h={110} tekst={getypt(q, f, t0, 2)} f={f} />
      <div style={{position: 'absolute', left: 0, right: 0, top: 590, textAlign: 'center', fontSize: 52, color: C.sub, opacity: ci(f, t0 + 12, t0 + 18)}}>
        <b style={{color: C.groen}}>{getal(ng, f, t0 + 12, t0 + 24)}</b> keer gezegd · <b style={{color: '#000'}}>{getal(ns, f, t0 + 12, t0 + 24)}</b> stukken
      </div>
      <div style={{position: 'absolute', left: 0, right: 0, top: 700, display: 'flex', justifyContent: 'center', gap: 14}}>
        {BREED.map((w, j) => <span key={w} style={{fontSize: 26, borderRadius: 999, padding: '8px 20px', background: j <= i ? C.zacht : '#fff', color: j <= i ? C.groenD : C.sub, fontWeight: j === i ? 700 : 400, ...inSchuif(f, 14 + j * per, 10)}}>{w}</span>)}
      </div>
      <Knipoog f={f} start={14 + 4 * per + 12} />
    </Scene>
  );
};

export const Deel2 = () => (
  <AbsoluteFill style={{background: C.grijs, fontFamily: F}}>
    <Sequence from={0} durationInFrames={300}><Diepte /></Sequence>
    <Sequence from={300} durationInFrames={210}><Breedte /></Sequence>
  </AbsoluteFill>
);
