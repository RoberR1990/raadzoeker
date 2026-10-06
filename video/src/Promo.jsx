// Promovideo raadzoeker, 60 s, 16:9. Alle cijfers en teksten komen uit data.json (python video/data.py).
import React from 'react';
import {AbsoluteFill, Sequence, useCurrentFrame, interpolate, spring, Easing} from 'remotion';
import D from './data.json';

export const NAAM = 'raadzoeker';
const LINK = 'raadzoeker.nl';
const C = {groen: '#00811F', groenD: '#004C31', zacht: '#E1EFE2', mid: '#4EB051', grijs: '#EFF4F6', grijs2: '#DBE7EA', lijn: '#CAD6DA', sub: '#3E4B50', water: '#D3E3EA'};
const F = 'Arial, Helvetica, sans-serif';
const FPS = 30;

// scènes: [begin, duur] in frames; ze overlappen 10 frames voor een zachte overgang
const S = {wolk: [0, 92], zoek: [90, 250], breed: [330, 280], park: [600, 310], belofte: [900, 220], gebied: [1110, 400], slot: [1500, 300]};
export const DUUR = 1800;

const ease = Easing.bezier(0.33, 0, 0.2, 1);
const ci = (f, a, b, c = 0, d = 1, e = ease) => interpolate(f, [a, b], [c, d], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: e});
const sp = (f, d = 0, cfg = {damping: 16, stiffness: 120}) => spring({frame: f - d, fps: FPS, config: cfg});
const nl = (n) => Math.round(n).toLocaleString('nl-NL');
const MND = ['januari', 'februari', 'maart', 'april', 'mei', 'juni', 'juli', 'augustus', 'september', 'oktober', 'november', 'december'];
const datum = (s) => {const [y, m, d] = s.split('-'); return `${+d} ${MND[+m - 1]} ${y}`;};
const tijd = (s) => [Math.floor(s / 3600), Math.floor(s / 60) % 60, s % 60].map((x, i) => (i ? String(x).padStart(2, '0') : x)).join(':');

const Scene = ({dur, children, bg = C.grijs, inn = true, uit = true}) => {
  const f = useCurrentFrame();
  const o = Math.min(inn ? ci(f, 0, 10) : 1, uit ? ci(f, dur - 10, dur, 1, 0) : 1);
  return <AbsoluteFill style={{background: bg, opacity: o, fontFamily: F, color: '#000', overflow: 'hidden'}}>{children}</AbsoluteFill>;
};

// logo: halfrond van negen zetels, één groen gemarkeerd (zoals op de site)
const Logo = ({h = 60, kleur = '#fff', accent = '#fff', t = 1}) => {
  const z = [];
  for (let i = 0; i < 9; i++) {
    const a = Math.PI * (1 - i / 8), x = 17 + 13 * Math.cos(a), y = 18 - 13 * Math.sin(a);
    const s = Math.max(0, Math.min(1, t * 9 - i));
    z.push(<circle key={i} cx={x} cy={y} r={2.6 * s} fill={i === 6 ? accent : kleur} opacity={i === 6 ? 1 : 0.75} />);
  }
  return <svg viewBox="0 0 34 20" style={{height: h, width: h * 1.7}}>{z}<circle cx="17" cy="17" r={3.2 * Math.min(1, t * 1.2)} fill={kleur} /></svg>;
};

// tekst in beeld: kop linksboven met groen streepje
const Kop = ({f, tekst, sub, d = 0, kleur = '#000'}) => (
  <div style={{position: 'absolute', left: 80, top: 56, opacity: ci(f, d, d + 12), transform: `translateY(${ci(f, d, d + 14, 24, 0)}px)`}}>
    <div style={{width: ci(f, d + 4, d + 20, 0, 72), height: 8, background: C.groen, borderRadius: 4, marginBottom: 16}} />
    <div style={{fontSize: 60, fontWeight: 700, color: kleur, lineHeight: 1.1}}>{tekst}</div>
    {sub && <div style={{fontSize: 30, color: C.sub, marginTop: 10, opacity: ci(f, d + 10, d + 22)}}>{sub}</div>}
  </div>
);

const Cursor = ({x, y, klik = -99, f}) => {
  const r = ci(f, klik, klik + 14, 0, 70), o = ci(f, klik, klik + 14, 0.5, 0);
  return (
    <div style={{position: 'absolute', left: x, top: y, pointerEvents: 'none'}}>
      {f >= klik && <div style={{position: 'absolute', left: -r, top: -r, width: 2 * r, height: 2 * r, borderRadius: '50%', background: C.groen, opacity: o}} />}
      <svg width="44" height="54" viewBox="0 0 22 27" style={{position: 'absolute', left: -4, top: -2, transform: `scale(${f >= klik && f < klik + 6 ? 0.85 : 1})`, filter: 'drop-shadow(0 3px 4px rgba(0,0,0,.35))'}}>
        <path d="M2 2 L2 22 L7 17 L11 25 L14.5 23.5 L10.5 15.5 L17.5 15.5 Z" fill="#fff" stroke="#000" strokeWidth="1.6" strokeLinejoin="round" />
      </svg>
    </div>
  );
};

const Zoekbalk = ({x, y, w, h = 104, tekst = '', caret = true, f = 0, knop = true}) => (
  <div style={{position: 'absolute', left: x, top: y, width: w, height: h, background: '#fff', borderRadius: h / 2, boxShadow: '0 18px 50px rgba(0,60,30,.16)', border: `2px solid ${C.lijn}`, display: 'flex', alignItems: 'center', paddingLeft: h * 0.42, boxSizing: 'border-box', overflow: 'hidden'}}>
    <svg width={h * 0.36} height={h * 0.36} viewBox="0 0 24 24" style={{flex: 'none'}}><circle cx="10" cy="10" r="7" fill="none" stroke={C.groen} strokeWidth="2.8" /><path d="M15.5 15.5 L22 22" stroke={C.groen} strokeWidth="2.8" strokeLinecap="round" /></svg>
    <div style={{fontSize: h * 0.4, marginLeft: h * 0.24, whiteSpace: 'nowrap', flex: 1, color: tekst ? '#000' : C.sub}}>
      {tekst}{caret && <span style={{display: 'inline-block', width: 3, height: h * 0.42, background: C.groen, marginLeft: 3, verticalAlign: 'middle', opacity: Math.floor(f / 15) % 2 ? 0.1 : 1}} />}
    </div>
    {knop && w > 600 && <div style={{background: C.groen, color: '#fff', fontWeight: 700, fontSize: h * 0.3, borderRadius: 999, padding: `${h * 0.17}px ${h * 0.34}px`, marginRight: h * 0.14, flex: 'none'}}>Zoek</div>}
  </div>
);

const Kaart = ({style, children}) => <div style={{position: 'absolute', background: '#fff', borderRadius: 18, boxShadow: '0 10px 34px rgba(0,40,20,.10)', padding: 32, boxSizing: 'border-box', ...style}}>{children}</div>;
const AI = ({children = 'AI-samenvatting'}) => <span style={{fontSize: 20, fontWeight: 400, background: C.grijs, borderRadius: 6, padding: '4px 12px', marginLeft: 14, verticalAlign: 'middle'}}>{children}</span>;

// markeer de woorden die de zoekopdracht raken
const Mark = ({tekst, rx = /(parkeer\w*|parkeren)/gi}) => tekst.split(rx).map((s, i) => (i % 2 ? <mark key={i} style={{background: C.zacht, color: C.groenD, fontWeight: 700, padding: '0 4px', borderRadius: 4}}>{s}</mark> : s));
const fragment = (t, n = 150) => {
  const z = t.split(/(?<=[.?!])\s+/), i = Math.max(0, z.findIndex((x) => /parkeer|parkeren/i.test(x)));
  let s = z[i]; if (s.length < 80 && z[i + 1]) s += ' ' + z[i + 1];
  return '…' + (s.length > n ? s.slice(0, n).replace(/\s\S*$/, '') + ' …' : s);
};

/* ---------- 1. woordenwolk -> zoekbalk ---------- */
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
const KLEUR = [C.groen, C.groenD, '#000', C.sub, C.groen, '#000'];
const Wolk = () => {
  const f = useCurrentFrame();
  const zoom = ci(f, 0, 60, 1.06, 1);
  const bw = ci(f, 58, 84, 0, 1200, Easing.out(Easing.cubic));
  return (
    <Scene dur={S.wolk[1]} inn={false} uit={false}>
      <AbsoluteFill style={{transform: `scale(${zoom})`}}>
        {WOLK.map(({w, fs, x, y, i}) => {
          const d = i * 0.9, s = sp(f, d, {damping: 14, stiffness: 140});
          const m = ci(f, 46 + (i % 9), 78 + (i % 9), 0, 1, Easing.in(Easing.cubic));
          const xx = x + (960 - x) * m, yy = y + (540 - y) * m;
          return <div key={w} style={{position: 'absolute', left: xx, top: yy, transform: `translate(-50%,-50%) scale(${s * (1 - 0.75 * m)})`, opacity: Math.min(s, 1 - m), fontSize: fs, fontWeight: i < 10 ? 700 : 400, color: KLEUR[i % 6], whiteSpace: 'nowrap'}}>{w}</div>;
        })}
      </AbsoluteFill>
      {bw > 2 && <Zoekbalk x={960 - bw / 2} y={488} w={bw} f={f} knop={bw > 1100} />}
    </Scene>
  );
};

/* ---------- 2. zoeken: parkeren ---------- */
const Zoeken = () => {
  const f = useCurrentFrame(), Z = D.zoek;
  const vraag = 'Wat zei de raad over parkeren?';
  const t = Z.q.slice(0, Math.floor(ci(f, 22, 48, 0, Z.q.length + 0.99, Easing.linear)));
  const op = ci(f, 56, 80, 0, 1, Easing.inOut(Easing.cubic));
  const bx = 360 + (80 - 360) * op, by = 488 + (170 - 488) * op, bw = 1200 + (1760 - 1200) * op, bh = 104 - 16 * op;
  const max = Math.max(...Z.per);
  const klik = 168, open = ci(f, klik + 6, klik + 30, 0, 1, Easing.out(Easing.cubic));
  const h0 = Z.hits[0];
  return (
    <Scene dur={S.zoek[1]} inn={false}>
      <div style={{position: 'absolute', left: 0, right: 0, top: 360 - 300 * op, textAlign: op > 0.5 ? 'left' : 'center', paddingLeft: op > 0.5 ? 80 : 0, fontSize: 72 - 20 * op, fontWeight: 700, opacity: ci(f, 0, 14)}}>{vraag}</div>
      <Zoekbalk x={bx} y={by} w={bw} h={bh} tekst={t} f={f} caret={f < 56} />
      {/* links: hoeveel en wanneer */}
      <Kaart style={{left: 80, top: 300, width: 600, height: 700, opacity: ci(f, 70, 84), transform: `translateY(${ci(f, 70, 88, 40, 0)}px)`}}>
        <div style={{fontSize: 24, color: C.sub}}>In debatten van raad en commissies</div>
        <div style={{fontSize: 92, fontWeight: 700, color: C.groen, lineHeight: 1.1}}>{nl(ci(f, 74, 110, 0, Z.n))}</div>
        <div style={{fontSize: 28, marginBottom: 34}}>keer over parkeren gesproken</div>
        <div style={{display: 'flex', alignItems: 'flex-end', gap: 14, height: 300}}>
          {Z.per.map((v, i) => <div key={i} style={{flex: 1, textAlign: 'center'}}>
            <div style={{height: 280 * (v / max) * ci(f, 84 + i * 3, 104 + i * 3), background: i === Z.per.length - 1 ? C.groen : C.mid, borderRadius: '6px 6px 0 0'}} />
            <div style={{fontSize: 19, color: C.sub, marginTop: 8}}>{"'" + Z.jaren[i].slice(2)}</div></div>)}
        </div>
        <div style={{fontSize: 22, color: C.sub, marginTop: 26}}>Per jaar · stand {datum(D.stand)}</div>
      </Kaart>
      {/* rechts: resultaten */}
      {Z.hits.map((h, i) => {
        const d = 84 + i * 10;
        return <Kaart key={i} style={{left: 720, top: 300 + i * 238, width: 1120, height: 218, padding: '24px 32px', opacity: ci(f, d, d + 12), transform: `translateX(${ci(f, d, d + 18, 80, 0)}px)`}}>
          <div style={{fontSize: 21, color: C.sub}}>{datum(h.datum)} · {h.verg}</div>
          <div style={{fontSize: 26, fontWeight: 700, margin: '4px 0 6px', width: 820, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis'}}>{h.punt}</div>
          <div style={{fontSize: 23, lineHeight: 1.4, height: 66, overflow: 'hidden'}}><b>{h.wie}{h.partij ? ` (${h.partij})` : ''}:</b> <Mark tekst={fragment(h.fragment, 130)} /></div>
          <div style={{position: 'absolute', right: 26, top: 20, background: i === 0 && f > klik ? C.groenD : C.groen, color: '#fff', fontSize: 20, fontWeight: 700, borderRadius: 999, padding: '10px 18px'}}>▶ Bekijk dit moment</div>
        </Kaart>;
      })}
      <Cursor f={f} klik={klik} x={ci(f, 130, 164, 1500, 1720, Easing.inOut(Easing.cubic))} y={ci(f, 130, 164, 900, 342, Easing.inOut(Easing.cubic))} />
      {/* videomoment */}
      {open > 0 && <AbsoluteFill style={{background: `rgba(0,0,0,${0.55 * open})`}}>
        <div style={{position: 'absolute', left: 960 - 640 * (0.3 + 0.7 * open) , top: 560 - 360 * (0.3 + 0.7 * open), width: 1280 * (0.3 + 0.7 * open), height: 720 * (0.3 + 0.7 * open), background: '#11181B', borderRadius: 16, overflow: 'hidden', opacity: open, boxShadow: '0 30px 80px rgba(0,0,0,.5)'}}>
          <div style={{transform: `scale(${0.3 + 0.7 * open})`, transformOrigin: '0 0', width: 1280, height: 720, position: 'relative', color: '#fff'}}>
            <div style={{position: 'absolute', left: 36, top: 28, fontSize: 26, opacity: 0.85}}>{h0.verg} · {datum(h0.datum)}</div>
            <div style={{position: 'absolute', left: 36, top: 66, fontSize: 30, fontWeight: 700, width: 1180}}>{h0.punt}</div>
            <svg style={{position: 'absolute', left: 0, top: 200}} width="1280" height="200">{Array.from({length: 64}, (_, i) => {const a = 20 + 70 * Math.abs(Math.sin(i * 0.9 + f * 0.35) * Math.cos(i * 0.37 + f * 0.11)); return <rect key={i} x={40 + i * 19} y={100 - a / 2} width="10" height={a} rx="5" fill={C.mid} opacity="0.8" />;})}</svg>
            <div style={{position: 'absolute', left: 80, right: 80, bottom: 120, textAlign: 'center', fontSize: 38, lineHeight: 1.35, background: 'rgba(0,0,0,.55)', padding: '12px 20px', borderRadius: 10}}>
              <b>{h0.wie}:</b> {fragment(h0.fragment, 120).replace(/^…/, '').slice(0, Math.floor(ci(f, klik + 26, klik + 50, 0, 140, Easing.linear)))}
            </div>
            <div style={{position: 'absolute', left: 36, right: 36, bottom: 40, height: 8, background: 'rgba(255,255,255,.2)', borderRadius: 4}}><div style={{width: `${78 + ci(f, klik, S.zoek[1], 0, 2)}%`, height: 8, background: C.mid, borderRadius: 4}} /></div>
            <div style={{position: 'absolute', right: 36, bottom: 60, fontSize: 24, opacity: 0.8}}>{tijd(h0.sec + Math.floor((f - klik) / FPS))}</div>
          </div>
        </div>
      </AbsoluteFill>}
    </Scene>
  );
};

/* ---------- 3. breed: alle domeinen, gebieden, jaren ---------- */
const Breed = () => {
  const f = useCurrentFrame();
  const qs = D.breed.slice(0, 4), per = 26, k = Math.min(qs.length - 1, Math.floor(f / per)), lf = f - k * per;
  const [q, n] = qs[k];
  const zw = ci(f, 104, 124, 1, 0);
  const max = Math.max(...D.domeinen.flatMap((d) => d[1]));
  const cw = 64, ch = 44, gx = 470, gy = 300;
  const tot = D.totaal;
  return (
    <Scene dur={S.breed[1]}>
      <Kop f={f} tekst="Elk onderwerp, elk gebied, sinds 2018" sub="13 domeinen · 14 gebieden · 8 jaar raad" />
      {zw > 0 && <div style={{opacity: zw}}>
        <Zoekbalk x={360} y={420} w={1200} f={f} tekst={q.slice(0, Math.ceil(ci(lf, 0, 9, 0, q.length, Easing.linear)))} caret />
        <div style={{position: 'absolute', left: 0, right: 0, top: 580, textAlign: 'center', fontSize: 44}}>
          <b style={{color: C.groen, fontSize: 64}}>{nl(ci(lf, 8, 18, 0, n))}</b> keer gezegd in de raad</div>
        <div style={{position: 'absolute', left: 0, right: 0, top: 680, display: 'flex', justifyContent: 'center', gap: 16}}>
          {qs.map(([x], i) => <div key={x} style={{fontSize: 26, padding: '8px 22px', borderRadius: 999, border: `2px solid ${i === k ? C.groen : C.lijn}`, background: i === k ? C.zacht : '#fff'}}>{x}</div>)}
        </div>
      </div>}
      {f > 100 && <div style={{opacity: ci(f, 104, 120)}}>
        {D.gebieden.map((g, j) => <div key={g} style={{position: 'absolute', left: gx + j * cw + 18, top: gy - 12, transformOrigin: '0 100%', transform: 'rotate(-42deg)', fontSize: 19, whiteSpace: 'nowrap', color: C.sub, opacity: ci(f, 110 + j, 124 + j)}}>{g}</div>)}
        {D.domeinen.map(([naam, v], r) => <React.Fragment key={naam}>
          <div style={{position: 'absolute', left: 80, width: gx - 100, top: gy + r * ch + 6, height: ch - 6, textAlign: 'right', fontSize: 22, lineHeight: `${ch - 6}px`, opacity: ci(f, 108 + r, 122 + r)}}>{naam}</div>
          {v.map((x, j) => {const s = sp(f, 112 + (r + j) * 1.6, {damping: 13, stiffness: 160}); const t = Math.sqrt(x / max);
            return <div key={j} style={{position: 'absolute', left: gx + j * cw, top: gy + r * ch, width: cw - 6, height: ch - 6, borderRadius: 6, background: interpolate(t, [0, 1], [0, 1]) > 0.5 ? C.groenD : C.groen, opacity: 0.12 + 0.88 * t, transform: `scale(${s})`}} />;})}
        </React.Fragment>)}
        {[[tot.beurten, 'debatbeurten'], [tot.stukken, 'officiële stukken'], [tot.vergaderingen, 'vergaderingen']].map(([n, l], i) =>
          <div key={l} style={{position: 'absolute', left: 1410, top: 330 + i * 190, opacity: ci(f, 150 + i * 14, 164 + i * 14), transform: `translateX(${ci(f, 150 + i * 14, 168 + i * 14, 40, 0)}px)`}}>
            <div style={{fontSize: 84, fontWeight: 700, color: C.groen, lineHeight: 1}}>{nl(ci(f, 150 + i * 14, 196 + i * 14, 0, n))}</div>
            <div style={{fontSize: 30}}>{l}</div></div>)}
        <div style={{position: 'absolute', left: 1410, top: 900, fontSize: 30, color: C.sub, opacity: ci(f, 200, 214)}}>2018 → {datum(D.stand)}</div>
      </div>}
    </Scene>
  );
};

/* ---------- 4. dossier Parkeren ---------- */
const Parkeren = () => {
  const f = useCurrentFrame(), P = D.parkeren, kern = P.kern.slice(0, 2);
  const hov = 110, tip = ci(f, hov + 8, hov + 22);
  const ak = ci(f, 190, 216, 0, 1, Easing.out(Easing.cubic));
  const z1 = kern[1];
  return (
    <Scene dur={S.park[1]}>
      <div style={{position: 'absolute', left: 80, top: 60, fontSize: 26, color: C.sub, opacity: ci(f, 0, 12)}}>Domeinen › Mobiliteit ›</div>
      <div style={{position: 'absolute', left: 80, top: 96, fontSize: 104, fontWeight: 700, opacity: ci(f, 4, 16), transform: `translateY(${ci(f, 4, 20, 20, 0)}px)`}}>Parkeren</div>
      <div style={{position: 'absolute', right: 80, top: 80, fontSize: 40, fontWeight: 700, color: C.groen, background: '#fff', borderRadius: 999, padding: '16px 34px', boxShadow: '0 8px 24px rgba(0,40,20,.1)', opacity: ci(f, hov, hov + 14), transform: `scale(${sp(f, hov)})`}}>Elke zin één klik van de bron</div>
      <Kaart style={{left: 80, top: 260, width: 1180 - 120 * ak, height: 760, borderTop: `8px solid ${C.groen}`}}>
        <div style={{fontSize: 34, fontWeight: 700, marginBottom: 20}}>In het kort <AI /></div>
        {kern.map((z, i) => <p key={i} style={{fontSize: 34, lineHeight: 1.45, margin: '0 0 22px', opacity: ci(f, 18 + i * 14, 32 + i * 14), transform: `translateY(${ci(f, 18 + i * 14, 34 + i * 14, 18, 0)}px)`}}>
          <span style={{background: i === 1 && f > hov ? C.zacht : 'transparent', borderBottom: `3px ${i === 1 && f > hov ? 'solid' : 'dotted'} ${C.mid}`, borderRadius: 4, padding: '0 2px'}}>{z.zin}</span></p>)}
      </Kaart>
      {tip > 0 && <div style={{position: 'absolute', left: 140, top: 640, width: 960, background: '#fff', borderRadius: 14, padding: '26px 30px', boxShadow: '0 24px 60px rgba(0,0,0,.22)', border: `2px solid ${C.groen}`, opacity: tip * (1 - ak * 0.0), transform: `translateY(${(1 - tip) * 20}px)`}}>
        <div style={{fontSize: 22, color: C.groen, fontWeight: 700, marginBottom: 8}}>Letterlijk citaat</div>
        <div style={{fontSize: 30, lineHeight: 1.4}}>‘{z1.citaat}’</div>
        <div style={{fontSize: 22, color: C.sub, marginTop: 12}}>{z1.bron_label} · {datum(z1.bron_datum)} · <u style={{color: C.groen}}>bron openen</u></div>
      </div>}
      <Cursor f={f} klik={hov} x={ci(f, 70, hov - 4, 1300, 700, Easing.inOut(Easing.cubic))} y={ci(f, 70, hov - 4, 900, 520, Easing.inOut(Easing.cubic))} />
      {ak > 0 && <Kaart style={{left: 1980 - 840 * ak, top: 260, width: 760, height: 760, borderTop: `8px solid ${C.groenD}`}}>
        <div style={{fontSize: 22, color: C.sub}}>Coalitieakkoord 2026–2030</div>
        <div style={{fontSize: 40, fontWeight: 700, marginBottom: 22}}>Wat belooft de coalitie?</div>
        {P.akkoord.map(([t, blz], i) => <div key={i} style={{display: 'flex', gap: 16, marginBottom: 20, opacity: ci(f, 214 + i * 16, 228 + i * 16)}}>
          <div style={{flex: 'none', fontSize: 20, fontWeight: 700, color: C.groenD, background: C.zacht, borderRadius: 6, padding: '4px 10px', height: 28}}>blz. {blz}</div>
          <div style={{fontSize: 25, lineHeight: 1.38}}>‘{t}’</div></div>)}
      </Kaart>}
    </Scene>
  );
};

/* ---------- 5. beloftes volgen ---------- */
const Beloftes = () => {
  const f = useCurrentFrame(), P = D.parkeren, M = P.moties, T = P.toez;
  const balk = (l, af, open, d) => {const tot = af + open, t = ci(f, d, d + 40);
    return <div style={{marginBottom: 46, opacity: ci(f, d - 6, d + 6)}}>
      <div style={{fontSize: 30, marginBottom: 12}}><b>{l}</b> <span style={{color: C.sub}}>· {nl(tot * t)}</span></div>
      <div style={{display: 'flex', height: 54, borderRadius: 10, overflow: 'hidden', background: C.grijs2}}>
        <div style={{width: `${(af / tot) * 100 * t}%`, background: C.groen}} /><div style={{width: `${(open / tot) * 100 * t}%`, background: C.mid, opacity: 0.45}} /></div>
      <div style={{display: 'flex', gap: 30, fontSize: 24, marginTop: 10}}><span><b style={{color: C.groen}}>{nl(af * t)}</b> afgedaan</span><span><b>{nl(open * t)}</b> nog open</span></div></div>;};
  const mo = P.motie, fr = mo ? Object.keys(mo[4]).sort((a, b) => a.localeCompare(b)) : [];
  return (
    <Scene dur={S.belofte[1]}>
      <Kop f={f} tekst="Volg de beloftes" sub="Wat de raad vroeg, wat het college toezegde, en of het gebeurde" />
      <Kaart style={{left: 80, top: 290, width: 740, height: 470}}>
        {balk('Aangenomen moties', M.afgedaan, M.open, 12)}
        {balk('Toezeggingen', T.afgedaan, T.open, 26)}
      </Kaart>
      {P.spoor.slice(0, 2).map((s, i) => {const d = 30 + i * 18; const st = s.stappen;
        return <Kaart key={i} style={{left: 860, top: 290 + i * 245, width: 980, height: 232, padding: '24px 32px', opacity: ci(f, d, d + 12), transform: `translateX(${ci(f, d, d + 18, 60, 0)}px)`}}>
          <div style={{fontSize: 21, color: C.sub}}>Toezegging · {s.wie} · {datum(s.datum)}</div>
          <div style={{fontSize: 28, fontWeight: 700, margin: '4px 0 26px'}}>{s.titel}</div>
          <div style={{position: 'relative', height: 84}}>
            <div style={{position: 'absolute', left: 14, right: 14, top: 12, height: 6, background: C.grijs2, borderRadius: 3}} />
            <div style={{position: 'absolute', left: 14, top: 12, height: 6, width: `${ci(f, d + 16, d + 60, 0, 50)}%`, background: C.groen, borderRadius: 3}} />
            {st.map(([dt, k, l], j) => {const on = j < st.length - 1; const x = (j / (st.length - 1)) * 100;
              return <div key={j} style={{position: 'absolute', left: `calc(${x}% - ${j === 0 ? 0 : j === st.length - 1 ? 30 : 15}px)`, top: 0, textAlign: j === 0 ? 'left' : j === st.length - 1 ? 'right' : 'center', transform: j === st.length - 1 ? 'translateX(-100%) translateX(30px)' : j ? 'translateX(-50%) translateX(15px)' : ''}}>
                <div style={{width: 30, height: 30, borderRadius: '50%', margin: j === 0 ? 0 : j === st.length - 1 ? '0 0 0 auto' : '0 auto', background: on && f > d + 16 + j * 22 ? C.groen : '#fff', border: `4px ${on ? 'solid' : 'dashed'} ${C.groen}`, boxSizing: 'border-box', transform: `scale(${on ? sp(f, d + 16 + j * 22) : 1})`}} />
                <div style={{fontSize: 20, marginTop: 6, whiteSpace: 'nowrap', color: on ? '#000' : C.sub, lineHeight: 1.25}}>{({toegezegd: 'Toegezegd', afdoeningsvoorstel: 'Voorstel afdoening', verwacht: 'Afdoening verwacht'})[k] || l}<br />{datum(dt).replace(/ 20\d\d$/, '')}</div></div>;})}
          </div>
        </Kaart>;})}
      {mo && <Kaart style={{left: 80, top: 800, width: 1760, height: 220, padding: '24px 32px', opacity: ci(f, 96, 110)}}>
        <div style={{fontSize: 24, color: C.sub}}>Hoe stemden de fracties? · {datum(mo[0])} · {mo[3] ? 'aangenomen' : 'verworpen'}</div>
        <div style={{fontSize: 28, fontWeight: 700, margin: '4px 0 18px'}}>Motie ‘{mo[1]}’</div>
        <div style={{display: 'flex', flexWrap: 'wrap', gap: 10}}>{fr.map((p, i) => {const v = mo[4][p] === 'v', s = sp(f, 108 + i * 3);
          return <div key={p} style={{fontSize: 20, padding: '6px 14px', borderRadius: 999, background: v ? C.groen : '#fff', color: v ? '#fff' : '#000', border: `2px solid ${v ? C.groen : C.lijn}`, transform: `scale(${s})`, opacity: s}}>{v ? '✓' : '✗'} {p}</div>;})}</div>
      </Kaart>}
    </Scene>
  );
};

/* ---------- 6. gebied: Delfshaven ---------- */
const bbox = (d) => {const n = (d.match(/-?\d+\.?\d*/g) || []).map(Number); let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
  for (let i = 0; i + 1 < n.length; i += 2) {x0 = Math.min(x0, n[i]); x1 = Math.max(x1, n[i]); y0 = Math.min(y0, n[i + 1]); y1 = Math.max(y1, n[i + 1]);} return [x0, y0, x1, y1];};
const Gebied = () => {
  const f = useCurrentFrame(), K = D.kaart, G = D.delfshaven;
  const dh = K.gebieden.find((g) => g[0] === 'Delfshaven'), [x0, y0, x1, y1] = bbox(dh[1]);
  // hele stad: kaart 1000x451 op 1.76x; ingezoomd: Delfshaven vult het linkervlak (60..900 x 180..1020)
  const z = ci(f, 66, 112, 0, 1, Easing.inOut(Easing.cubic));
  const s0 = 1.76, tx0 = 960 - 500 * s0, ty0 = 610 - 225 * s0;
  const s1 = Math.min(820 / (x1 - x0), 780 / (y1 - y0)), tx1 = 480 - ((x0 + x1) / 2) * s1, ty1 = 600 - ((y0 + y1) / 2) * s1;
  const sc = s0 + (s1 - s0) * z, tx = tx0 + (tx1 - tx0) * z, ty = ty0 + (ty1 - ty0) * z;
  const cx = (x0 + x1) / 2 * s0 + tx0, cy = (y0 + y1) / 2 * s0 + ty0, klik = 54;
  const rd = ci(f, 112, 132, 0, 1, Easing.out(Easing.cubic));
  const inw = G.wijken.reduce((a, w) => a + (w.inw || 0), 0);
  const dom = G.domeinen.slice(0, 6), dmax = dom[0][1];
  const wr = G.wijkraad.filter(([, t]) => !/overleg|afschrift/i.test(t)).slice(0, 2);
  return (
    <Scene dur={S.gebied[1]}>
      <svg width="1920" height="1080" style={{position: 'absolute', left: 0, top: 0}}>
        <g transform={`translate(${tx},${ty}) scale(${sc})`}>
          <path d={K.water} fill={C.water} />
          <path d={K.havens} fill={C.water} opacity="0.7" />
          {K.gebieden.map(([n, d]) => {const dhv = n === 'Delfshaven', aan = dhv && f >= klik;
            return <path key={n} d={d} fill={aan ? C.groen : '#fff'} fillOpacity={aan ? 1 - 0.85 * rd : 1} stroke={C.lijn} strokeWidth={1.2 / sc * 1.76} opacity={dhv ? 1 : 1 - 0.75 * z} />;})}
          {rd > 0 && G.wijken.map((w, i) => <path key={w.naam} d={w.d} fill={C.groen} fillOpacity={0.12 + 0.1 * (i % 3)} stroke={C.groenD} strokeWidth={2 / sc} opacity={ci(f, 112 + i * 3, 124 + i * 3)} />)}
        </g>
      </svg>
      {rd > 0 && G.wijken.map((w, i) => <div key={w.naam} style={{position: 'absolute', left: w.lx * sc + tx, top: w.ly * sc + ty, transform: 'translate(-50%,-50%)', fontSize: 22, fontWeight: 700, color: C.groenD, textAlign: 'center', width: 170, lineHeight: 1.15, opacity: ci(f, 120 + i * 3, 132 + i * 3), textShadow: '0 0 6px #fff,0 0 6px #fff'}}>{w.naam.replace(' / ', ' /\n')}</div>)}
      {f < 100 && <div style={{opacity: ci(f, 86, 100, 1, 0)}}><Kop f={f} tekst="Wat speelt er in jouw wijk?" /></div>}
      {f < 66 && K.gebieden.map(([n, d]) => {if (!['Delfshaven', 'Centrum', 'Charlois', 'Feijenoord', 'Noord'].includes(n)) return null; const [a, b, c, e] = bbox(d);
        return <div key={n} style={{position: 'absolute', left: (a + c) / 2 * s0 + tx0, top: (b + e) / 2 * s0 + ty0, transform: 'translate(-50%,-50%)', fontSize: 22, fontWeight: n === 'Delfshaven' ? 700 : 400, color: n === 'Delfshaven' && f >= klik ? '#fff' : C.sub, opacity: ci(f, 6, 18) * ci(f, 56, 66, 1, 0)}}>{n}</div>;})}
      <Cursor f={f} klik={klik} x={ci(f, 14, klik - 4, 1500, cx + 10, Easing.inOut(Easing.cubic))} y={ci(f, 14, klik - 4, 950, cy + 10, Easing.inOut(Easing.cubic))} />
      {/* rechterkolom: de gebiedspagina */}
      {rd > 0 && <div style={{position: 'absolute', left: 960, top: 60, width: 880, opacity: rd, transform: `translateX(${(1 - rd) * 60}px)`}}>
        <div style={{fontSize: 24, color: C.sub}}>Gebieden ›</div>
        <div style={{fontSize: 92, fontWeight: 700, lineHeight: 1.05}}>Delfshaven</div>
        <div style={{fontSize: 28, color: C.sub, marginTop: 6}}>{G.wijken.length} wijken · {nl(inw)} inwoners (CBS 2024)</div>
        <Kaart style={{position: 'relative', marginTop: 28, padding: '24px 30px', borderTop: `8px solid ${C.groen}`}}>
          <div style={{fontSize: 26, fontWeight: 700, marginBottom: 10}}>Wat speelt er <AI /></div>
          <div style={{fontSize: 27, lineHeight: 1.42}}>{G.kern[0].zin}</div>
        </Kaart>
        <Kaart style={{position: 'relative', marginTop: 22, padding: '22px 30px', opacity: ci(f, 170, 184)}}>
          <div style={{fontSize: 26, fontWeight: 700, marginBottom: 14}}>Waar praat de raad over?</div>
          {dom.map(([n, v], i) => <div key={n} style={{display: 'flex', alignItems: 'center', gap: 14, marginBottom: 8}}>
            <div style={{width: 260, fontSize: 22, textAlign: 'right'}}>{n}</div>
            <div style={{height: 26, borderRadius: 4, background: i ? C.mid : C.groen, width: 420 * (v / dmax) * ci(f, 176 + i * 5, 206 + i * 5)}} />
            <div style={{fontSize: 20, color: C.sub, opacity: ci(f, 196 + i * 5, 206 + i * 5)}}>{nl(v)}</div></div>)}
        </Kaart>
        <Kaart style={{position: 'relative', marginTop: 22, padding: '22px 30px', opacity: ci(f, 250, 264)}}>
          <div style={{fontSize: 26, fontWeight: 700, marginBottom: 10}}>Wat vraagt de wijkraad?</div>
          {wr.map(([dt, t], i) => <div key={i} style={{fontSize: 23, padding: '8px 0', borderTop: i ? `1px solid ${C.grijs2}` : 'none', opacity: ci(f, 258 + i * 10, 270 + i * 10)}}><span style={{color: C.sub}}>{datum(dt)} · </span>{t}</div>)}
        </Kaart>
      </div>}
    </Scene>
  );
};

/* ---------- 7. slot ---------- */
const Slot = () => {
  const f = useCurrentFrame();
  const r = [['Elke bewering één klik van de bron', 44], ['Actueel: elke paar uur bijgewerkt', 58], ['Vibecode-experiment · open data · open source', 72]];
  return (
    <Scene dur={S.slot[1]} bg={C.groen} uit={false}>
      <div style={{position: 'absolute', left: 0, right: 0, top: 150, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 34, color: '#fff'}}>
        <Logo h={120} t={ci(f, 4, 30, 0, 1, Easing.linear)} accent="#B8E0BA" />
        <div style={{fontSize: 150, fontWeight: 700, letterSpacing: -2, opacity: ci(f, 16, 30), transform: `translateX(${ci(f, 16, 34, 30, 0)}px)`}}>{NAAM}</div>
      </div>
      <div style={{position: 'absolute', left: 0, right: 0, top: 380, textAlign: 'center', color: '#fff'}}>
        {r.map(([t, d]) => <div key={t} style={{fontSize: 46, margin: '0 0 18px', opacity: ci(f, d, d + 12), transform: `translateY(${ci(f, d, d + 16, 20, 0)}px)`}}>{t}</div>)}
      </div>
      <div style={{position: 'absolute', left: 0, right: 0, top: 690, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 20}}>
        <div style={{background: '#fff', color: C.groenD, fontSize: 60, fontWeight: 700, borderRadius: 999, padding: '22px 56px', transform: `scale(${sp(f, 96, {damping: 11, stiffness: 140})})`}}>{LINK}</div>
        <div style={{color: '#fff', fontSize: 34, opacity: ci(f, 112, 126)}}>Inloggen met je @rotterdam.nl-adres</div>
      </div>
      <div style={{position: 'absolute', left: 0, right: 0, bottom: 40, textAlign: 'center', color: '#fff', opacity: 0.75 * ci(f, 130, 150), fontSize: 24}}>Onofficieel hulpmiddel · gegevens van gemeenteraad.rotterdam.nl, CBS en Kadaster</div>
    </Scene>
  );
};

export const Promo = () => (
  <AbsoluteFill style={{background: C.grijs}}>
    <Sequence from={S.wolk[0]} durationInFrames={S.wolk[1]}><Wolk /></Sequence>
    <Sequence from={S.zoek[0]} durationInFrames={S.zoek[1]}><Zoeken /></Sequence>
    <Sequence from={S.breed[0]} durationInFrames={S.breed[1]}><Breed /></Sequence>
    <Sequence from={S.park[0]} durationInFrames={S.park[1]}><Parkeren /></Sequence>
    <Sequence from={S.belofte[0]} durationInFrames={S.belofte[1]}><Beloftes /></Sequence>
    <Sequence from={S.gebied[0]} durationInFrames={S.gebied[1]}><Gebied /></Sequence>
    <Sequence from={S.slot[0]} durationInFrames={S.slot[1]}><Slot /></Sequence>
  </AbsoluteFill>
);
