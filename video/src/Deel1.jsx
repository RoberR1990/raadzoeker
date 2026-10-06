// Promovideo v4, deel 1 (0–28 s), in de stijl van v1: nagebouwde schermen in de huisstijl, gevuld met echte data (src/d1.json),
// plus een echte clip uit de raadzaal (public/rec/pro.mp4, het citaat van PRO bij de Discriminatiemonitor, 1 oktober 2026).
import React from 'react';
import {AbsoluteFill, Sequence, Img, OffthreadVideo, staticFile, useCurrentFrame, interpolate, spring, Easing} from 'remotion';
import D from './data.json';
import X from './d1.json';

const C = {groen: '#00811F', groenD: '#004C31', zacht: '#E1EFE2', mid: '#4EB051', grijs: '#EFF4F6', grijs2: '#DBE7EA', lijn: '#CAD6DA', sub: '#3E4B50', navy: '#0E2A4D', blauw: '#00548F', rood: '#C0392B'};
const F = 'Arial, Helvetica, sans-serif';
const FPS = 30;
export const DUUR1 = 930;
const ease = Easing.bezier(0.33, 0, 0.2, 1);
const ci = (f, a, b, c = 0, d = 1, e = ease) => interpolate(f, [a, b], [c, d], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: e});
const sp = (f, d = 0, cfg = {damping: 16, stiffness: 120}) => spring({frame: f - d, fps: FPS, config: cfg});
const inSchuif = (f, d, afstand = 40) => ({opacity: ci(f, d, d + 12), transform: `translateY(${ci(f, d, d + 16, afstand, 0)}px)`});

const Scene = ({dur, children, bg = C.grijs}) => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{background: bg, opacity: Math.min(ci(f, 0, 10), ci(f, dur - 10, dur, 1, 0)), fontFamily: F, color: '#000', overflow: 'hidden'}}>{children}</AbsoluteFill>;
};
const Kop = ({f, tekst, sub, d = 0}) => (
  <div style={{position: 'absolute', left: 90, top: 64, ...inSchuif(f, d, 24)}}>
    <div style={{width: ci(f, d + 4, d + 20, 0, 72), height: 8, background: C.groen, borderRadius: 4, marginBottom: 16}} />
    <div style={{fontSize: 60, fontWeight: 700, lineHeight: 1.1}}>{tekst}</div>
    {sub && <div style={{fontSize: 30, color: C.sub, marginTop: 10, opacity: ci(f, d + 10, d + 22)}}>{sub}</div>}
  </div>
);
const Kaart = ({style, children}) => <div style={{position: 'absolute', background: '#fff', borderRadius: 18, boxShadow: '0 12px 40px rgba(0,40,20,.10)', padding: 36, boxSizing: 'border-box', ...style}}>{children}</div>;
const Chip = ({children, style}) => <span style={{display: 'inline-block', fontSize: 30, background: C.grijs, borderRadius: 8, padding: '6px 14px', margin: '0 8px 10px 0', ...style}}>{children}</span>;
const Cursor = ({x, y, klik = -99, f}) => {
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

/* 0–5.5 s: woordenwolk (rustig) trekt samen tot het logo */
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
  const lg = sp(f, 104, {damping: 14, stiffness: 90});
  return (
    <AbsoluteFill style={{background: C.grijs, fontFamily: F, opacity: ci(f, 185, 195, 1, 0)}}>
      <AbsoluteFill style={{transform: `scale(${ci(f, 0, 90, 1.05, 1)})`}}>
        {WOLK.map(({w, fs, x, y, i}) => {
          const s = sp(f, i * 1.3, {damping: 18, stiffness: 90}), m = ci(f, 72 + (i % 11), 108 + (i % 11), 0, 1, Easing.in(Easing.cubic));
          return <div key={w} style={{position: 'absolute', left: x + (960 - x) * m, top: y + (440 - y) * m, transform: `translate(-50%,-50%) scale(${s * (1 - 0.8 * m)})`,
            opacity: Math.min(s, 1 - m), fontSize: fs, fontWeight: i < 10 ? 700 : 400, color: KLEUR[i % 6], whiteSpace: 'nowrap'}}>{w}</div>;
        })}
      </AbsoluteFill>
      <div style={{position: 'absolute', left: 960, top: 440, transform: `translate(-50%,-50%) scale(${lg})`, opacity: Math.min(1, lg)}}>
        <Img src={staticFile('logo.svg')} style={{width: 360}} />
      </div>
      <div style={{position: 'absolute', left: 0, right: 0, top: 620, textAlign: 'center', fontSize: 96, fontWeight: 700, color: C.navy, ...inSchuif(f, 116, 20)}}>raadzoeker</div>
      <div style={{position: 'absolute', left: 0, right: 0, top: 738, textAlign: 'center', fontSize: 38, color: C.sub, ...inSchuif(f, 128, 14)}}>wat de Rotterdamse raad zegt, besluit en belooft</div>
    </AbsoluteFill>
  );
};

/* 5.5–10 s: overzicht Vergaderingen */
const Overzicht = () => {
  const f = useCurrentFrame(), R = X.raad;
  return (
    <Scene dur={135}>
      <Kop f={f} tekst="Elke vergadering samengevat" sub="Raad en commissies, kort na de vergadering" />
      <Kaart style={{left: 90, top: 260, width: 1060, height: 700, borderTop: `8px solid ${C.groen}`, ...inSchuif(f, 6)}}>{/* onderwerpen als chips */}
        <span style={{background: C.groen, color: '#fff', fontWeight: 700, fontSize: 22, borderRadius: 999, padding: '5px 16px'}}>Laatste raadsvergadering</span>
        <span style={{fontSize: 24, color: C.sub, marginLeft: 14}}>{R.datum}</span>
        <div style={{fontSize: 52, fontWeight: 700, margin: '22px 0 26px'}}>Wat besprak de raad?</div>
        <div>{R.ap.map((t, i) => <Chip key={t} style={{...inSchuif(f, 20 + i * 5, 14), display: 'inline-block'}}>{t}</Chip>)}</div>
        <div style={{position: 'absolute', left: 36, bottom: 40, background: C.groen, color: '#fff', fontWeight: 700, fontSize: 28, borderRadius: 999, padding: '16px 34px', ...inSchuif(f, 70, 14)}}>Lees in 1 minuut</div>
      </Kaart>
      <Kaart style={{left: 1190, top: 260, width: 640, height: 700, borderTop: `8px solid ${C.blauw}`, ...inSchuif(f, 14)}}>
        <div style={{fontSize: 34, fontWeight: 700, marginBottom: 18}}>Komt eraan</div>
        {X.komt.map(([n, d, p], i) => (
          <div key={i} style={{borderTop: `2px solid ${C.grijs2}`, padding: '18px 0', ...inSchuif(f, 34 + i * 10, 20)}}>
            <div style={{fontSize: 26, fontWeight: 700}}>{n.replace(/^Commissie /, '')} <span style={{fontWeight: 400, color: C.sub, fontSize: 22}}>{+d.slice(8)} okt</span></div>
            <div style={{fontSize: 22, color: C.sub, marginTop: 6}}>{p.join(' · ')}</div>
          </div>
        ))}
      </Kaart>
      <Cursor x={ci(f, 70, 104, 1500, 270)} y={ci(f, 70, 104, 1040, 905)} klik={110} f={f} />
    </Scene>
  );
};

/* 10–15.5 s: kort (1 minuut) of uitgebreid (11 minuten) */
const Kort = () => {
  const f = useCurrentFrame(), al = X.raad.kort.slice(0, 2), uit = f >= 120;
  let n = 0;
  return (
    <Scene dur={215}>
      <Kop f={f} tekst="Lees de samenvatting in 1 minuut" sub="of de uitgebreide versie in 10 minuten" />
      <div style={{position: 'absolute', left: 90, top: 250, display: 'flex', background: C.grijs2, borderRadius: 999, padding: 6, ...inSchuif(f, 4, 14)}}>
        {[['Kort', '1 min'], ['Uitgebreid', `${X.raad.lees.uitgebreid} min`]].map(([a, b], i) => (
          <div key={a} style={{fontSize: 28, fontWeight: 700, padding: '12px 30px', borderRadius: 999, background: (i === 1) === uit ? '#fff' : 'transparent', boxShadow: (i === 1) === uit ? '0 3px 10px rgba(0,0,0,.12)' : 'none'}}>
            {a} <span style={{fontWeight: 400, color: C.sub, fontSize: 22}}>{b}</span></div>
        ))}
      </div>
      <Kaart style={{left: 90, top: 350, width: 1740, height: 640, borderTop: `8px solid ${C.groen}`, ...inSchuif(f, 8)}}>
        {al.map((zinnen, a) => (
          <p key={a} style={{fontSize: 33, lineHeight: 1.55, margin: '0 0 24px', maxWidth: 1600}}>
            {zinnen.map((z) => {const d = 16 + (n++) * 14, hl = ci(f, d + 6, d + 20); return <span key={z} style={{opacity: ci(f, d, d + 10, 0.15, 1), background: `linear-gradient(90deg, ${C.zacht} ${hl * 100}%, transparent ${hl * 100}%)`, borderRadius: 4}}>{z} </span>;})}
          </p>
        ))}
      </Kaart>
      <Cursor x={ci(f, 96, 116, 1300, 420)} y={ci(f, 96, 116, 900, 290)} klik={118} f={f} />
    </Scene>
  );
};

/* 15.5–23 s: tik op een fractie -> letterlijk citaat -> het moment in de video */
const Fractie = () => {
  const f = useCurrentFrame(), A = X.ap;
  const open = ci(f, 58, 74), zoom = ci(f, 132, 160), vid = f >= 132;
  return (
    <Scene dur={225}>
      <Kop f={f} tekst="Wie zei wat, letterlijk" sub="Tik op een fractie en kijk het moment terug" />
      <Kaart style={{left: 90, top: 250, width: 1740, height: 760, ...inSchuif(f, 6), opacity: Math.min(ci(f, 6, 18), 1 - zoom)}}>
        <div style={{fontSize: 46, fontWeight: 700}}>{A.titel}</div>
        <div style={{fontSize: 24, color: C.sub, margin: '8px 0 22px'}}>{A.tijd} · <span style={{color: C.groen, fontWeight: 700}}>▶ Bekijk dit onderwerp</span></div>
        <div style={{fontSize: 22, color: C.sub, fontWeight: 700, marginBottom: 6}}>Wat zeiden de fracties?</div>
        {A.fr.map(([w, p], i) => (
          <div key={w}>
            <div style={{display: 'grid', gridTemplateColumns: '300px 1fr', padding: '14px 0', borderTop: `2px solid ${C.grijs2}`, fontSize: 28, ...inSchuif(f, 16 + i * 6, 16), background: i === 0 && f > 50 ? C.zacht : 'transparent'}}>
              <b>{w}</b><span>{p}</span>
            </div>
            {i === 0 && open > 0 && (
              <div style={{marginLeft: 300, height: 120 * open, overflow: 'hidden'}}>
                <div style={{background: C.grijs, borderLeft: `6px solid ${C.groen}`, borderRadius: 8, padding: '16px 22px', fontSize: 28, lineHeight: 1.4}}>
                  ‘{A.pro.citaat}’
                  <div style={{fontSize: 22, color: C.sub, marginTop: 6}}>{A.pro.wie} · <span style={{color: C.groen, fontWeight: 700, transform: `scale(${1 + 0.06 * Math.sin(f / 4) * ci(f, 80, 90)})`, display: 'inline-block'}}>▶ bekijk dit moment (1:52:37)</span></div>
                </div>
              </div>
            )}
          </div>
        ))}
      </Kaart>
      {!vid && <Cursor x={f < 60 ? ci(f, 26, 52, 1400, 190) : ci(f, 84, 112, 190, 760)} y={f < 60 ? ci(f, 26, 52, 950, 482) : ci(f, 84, 112, 482, 640)} klik={f < 60 ? 54 : 118} f={f} />}
      {vid && (
        <div style={{position: 'absolute', left: interpolate(zoom, [0, 1], [700, 160]), top: interpolate(zoom, [0, 1], [600, 230]), width: interpolate(zoom, [0, 1], [480, 1600]),
          borderRadius: 16, overflow: 'hidden', boxShadow: '0 30px 80px rgba(0,0,0,.35)', background: '#000', opacity: zoom}}>
          <div style={{background: '#fff', fontSize: 24, fontWeight: 700, padding: '12px 20px'}}>Gemeenteraad · 1 oktober 2026 · {A.pro.wie}</div>
          <OffthreadVideo src={staticFile('rec/pro.mp4')} startFrom={20} muted style={{width: '100%', display: 'block'}} />
        </div>
      )}
    </Scene>
  );
};

/* 23–28 s: moties met uitslag en het spoor van commissie naar raad */
const BADGE = {Aangenomen: [C.groen, '#fff'], Verworpen: [C.grijs2, '#000'], Ingetrokken: [C.grijs2, C.sub]};
const Moties = () => {
  const f = useCurrentFrame(), M = X.mo, T = M.tl;
  return (
    <Scene dur={160}>
      <Kop f={f} tekst="Van commissie tot besluit" sub="Moties met uitslag, en waar het eerder besproken is" />
      <Kaart style={{left: 90, top: 250, width: 1060, height: 760, ...inSchuif(f, 6)}}>
        <div style={{fontSize: 22, color: C.sub, fontWeight: 700}}>Gemeenteraad · {M.datum}</div>
        <div style={{fontSize: 40, fontWeight: 700, margin: '6px 0 22px'}}>{M.titel}</div>
        {M.rijen.map(([u, t, p], i) => {const [bg, fg] = BADGE[u] || BADGE.Verworpen, s = sp(f, 22 + i * 7, {damping: 12, stiffness: 160});
          return (<div key={t} style={{display: 'flex', alignItems: 'center', gap: 16, padding: '11px 0', borderTop: `2px solid ${C.grijs2}`, fontSize: 26, opacity: ci(f, 18 + i * 7, 28 + i * 7)}}>
            <span style={{flex: 'none', width: 170, textAlign: 'center', background: bg, color: fg, fontWeight: 700, fontSize: 20, borderRadius: 999, padding: '5px 0', transform: `scale(${s})`}}>{u}</span>
            <span style={{flex: 1, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis'}}>{t} <span style={{color: C.sub, fontSize: 20}}>· {p}</span></span></div>);})}
      </Kaart>
      <Kaart style={{left: 1190, top: 250, width: 640, height: 760, ...inSchuif(f, 14)}}>
        <div style={{fontSize: 30, fontWeight: 700, marginBottom: 6}}>{M.titel}</div>
        <div style={{fontSize: 22, color: C.sub, marginBottom: 30}}>Dit onderwerp in de raad en commissies</div>
        <div style={{position: 'relative', paddingLeft: 40}}>
          <div style={{position: 'absolute', left: 13, top: 14, width: 4, height: ci(f, 40, 110, 0, (T.length - 1) * 150), background: C.mid, borderRadius: 2}} />
          {T.map((t, i) => {const s = sp(f, 40 + i * 30, {damping: 12, stiffness: 150}), hier = t[6];
            return (<div key={i} style={{position: 'relative', height: 150, opacity: ci(f, 40 + i * 30, 52 + i * 30)}}>
              <div style={{position: 'absolute', left: -38, top: 6, width: 26, height: 26, borderRadius: '50%', background: hier ? C.groen : '#fff', border: `4px solid ${hier ? C.groen : C.mid}`, transform: `scale(${s})`}} />
              <div style={{fontSize: 22, color: C.sub}}>{+t[0].slice(8)} {['jan', 'feb', 'mrt', 'apr', 'mei', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov', 'dec'][+t[0].slice(5, 7) - 1]}</div>
              <div style={{fontSize: 28, fontWeight: hier ? 700 : 400}}>{t[1].replace(/^Commissie /, 'Commissie ')}</div>
            </div>);})}
        </div>
      </Kaart>
    </Scene>
  );
};

export const Deel1 = () => (
  <AbsoluteFill style={{background: C.grijs}}>
    <Sequence from={0} durationInFrames={195}><Intro /></Sequence>
    <Sequence from={195} durationInFrames={135}><Overzicht /></Sequence>
    <Sequence from={330} durationInFrames={215}><Kort /></Sequence>
    <Sequence from={545} durationInFrames={225}><Fractie /></Sequence>
    <Sequence from={770} durationInFrames={160}><Moties /></Sequence>
  </AbsoluteFill>
);
