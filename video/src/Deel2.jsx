// Promovideo v4, deel 2 (16 s): Zoeken. 'Niet lullen, maar zoeken.' Echte resultaten uit de site (src/d2.json).
import React from 'react';
import {AbsoluteFill, Sequence, useCurrentFrame} from 'remotion';
import {C, F, ci, sp, inSchuif, Scene, Kop, Kaart, Zoekbalk, getypt, Mark, zinnen} from './stijl';
import X from './d2.json';

export const DUUR2 = 480;
const W = X.woonfraude, FY = X.Feyenoord;
const getal = (s, f, a, b) => Math.round(+s.replace(/\./g, '') * ci(f, a, b)).toLocaleString('nl-NL');

const Fragment = ({k, woord, f, d, style}) => (
  <Kaart style={{padding: '26px 32px', ...style, ...inSchuif(f, d, 30)}}>
    <div style={{fontSize: 22, color: C.sub}}>{k.waar} · {k.datum} · <b style={{color: '#000'}}>{k.wie}</b></div>
    <div style={{fontSize: 22, color: C.sub, marginTop: 4, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis'}}>{k.titel}</div>
    <div style={{fontSize: 30, lineHeight: 1.45, marginTop: 12}}>‘<Mark tekst={zinnen(k.citaat, woord)} woord={woord} />’</div>
    <div style={{fontSize: 22, color: C.groen, fontWeight: 700, marginTop: 10}}>▶ Bekijk dit moment</div>
  </Kaart>
);
const Tellers = ({ng, ns, f, d}) => (
  <div style={{position: 'absolute', left: 1130, top: 250, display: 'flex', gap: 14, ...inSchuif(f, d, 14)}}>
    {[['Gezegd', ng], ['Stukken', ns]].map(([a, n], i) => (
      <div key={a} style={{fontSize: 28, fontWeight: 700, background: i ? '#fff' : C.groen, color: i ? '#000' : '#fff', borderRadius: 999, padding: '12px 26px', boxShadow: '0 4px 14px rgba(0,0,0,.08)'}}>
        {a} <span style={{fontWeight: 400, opacity: 0.85}}>{getal(n, f, d, d + 30)}</span></div>
    ))}
  </div>
);

// rood-witte confetti (zoals op de site bij 'Feyenoord')
const STUK = Array.from({length: 140}, (_, i) => ({x: (i * 97) % 1920, v: 6 + ((i * 37) % 9), r: (i * 53) % 360, d: (i * 7) % 20, w: 14 + (i % 4) * 4, k: i % 2}));
const Confetti = ({f, start}) => f < start ? null : (
  <AbsoluteFill style={{pointerEvents: 'none'}}>
    {STUK.map((s, i) => {const t = f - start - s.d; if (t < 0) return null; const y = -40 + t * s.v * 1.6, x = s.x + Math.sin((t + i) / 7) * 30;
      return <div key={i} style={{position: 'absolute', left: x, top: y, width: s.w, height: s.w * 0.45, background: s.k ? C.rood : '#fff', border: s.k ? 'none' : `1px solid ${C.lijn}`, transform: `rotate(${s.r + t * 9}deg)`, opacity: ci(f, start + 70, start + 95, 1, 0)}} />;})}
  </AbsoluteFill>
);

const Zoeken = () => {
  const f = useCurrentFrame();
  // 0–75: grote titel; 75–300: woonfraude; 300–480: Feyenoord
  const omhoog = ci(f, 62, 84), fey = f >= 300;
  const tekst = f < 300 ? getypt('woonfraude', f, 90) : getypt('Feyenoord', f, 312);
  const titel = ci(f, 0, 14) * ci(f, 60, 74, 1, 0);
  return (
    <Scene dur={DUUR2}>
      <div style={{position: 'absolute', left: 0, right: 0, top: 330, textAlign: 'center', fontSize: 104, fontWeight: 700, color: C.navy, opacity: titel, transform: `scale(${0.92 + 0.08 * sp(f, 0)})`}}>Niet lullen, maar zoeken.</div>
      <Kop f={f} d={84} uit={290} tekst="Zoek in alles wat de raad zei en schreef" sub="Debatten, moties, brieven en raadsvoorstellen, sinds 2018" />
      <Kop f={f} d={312} tekst="Ook als het over Feyenoord gaat" sub="Elk zoekwoord, elk moment in de vergadering" />
      <Zoekbalk x={ci(omhoog, 0, 1, 380, 90)} y={ci(omhoog, 0, 1, 560, 236)} w={ci(omhoog, 0, 1, 1160, 1000)} h={ci(omhoog, 0, 1, 112, 88)} tekst={tekst} f={f} />
      {!fey && <>
        <Tellers ng={W.ng} ns={W.ns} f={f} d={130} />
        <Kaart style={{left: 90, top: 360, width: 1740, height: 220, borderTop: `8px solid ${C.groen}`, padding: '24px 34px', ...inSchuif(f, 140)}}>
          <div style={{fontSize: 30, fontWeight: 700}}>Uit de vergaderverslagen</div>
          <div style={{fontSize: 22, color: C.sub, marginTop: 10}}>{W.verslag[0][0]}</div>
          <div style={{fontSize: 32, fontWeight: 700, color: C.groen, marginTop: 4}}>{W.verslag[0][1]}</div>
          <div style={{fontSize: 24, color: C.sub, marginTop: 6, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis'}}>{W.verslag[0][2]}</div>
        </Kaart>
        <Fragment k={W.kaarten[1]} woord="woonfraude" f={f} d={170} style={{left: 90, top: 610, width: 850, height: 420}} />
        <Fragment k={W.kaarten[2]} woord="woonfraude" f={f} d={185} style={{left: 980, top: 610, width: 850, height: 420}} />
      </>}
      {fey && <>
        <Tellers ng={FY.ng} ns={FY.ns} f={f} d={350} />
        <Fragment k={FY.kaarten[0]} woord="Feyenoord" f={f} d={365} style={{left: 90, top: 360, width: 1740, height: 300}} />
        <Fragment k={FY.kaarten[1]} woord="Feyenoord" f={f} d={380} style={{left: 90, top: 690, width: 1740, height: 300}} />
        <Confetti f={f} start={346} />
      </>}
    </Scene>
  );
};

export const Deel2 = () => <AbsoluteFill style={{background: C.grijs, fontFamily: F}}><Sequence from={0} durationInFrames={DUUR2}><Zoeken /></Sequence></AbsoluteFill>;
