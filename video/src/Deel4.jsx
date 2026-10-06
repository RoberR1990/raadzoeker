// Promovideo v4, deel 4 (14 s): bonus. De Verkenner (kennisgraaf van alles wat gezegd en geschreven is): rustig inzoomen op
// 'Feyenoord City en stadion', buren lichten op, route naar 'Parkeren'. Daarna een flits van Inzichten. Echte data (src/d4.json).
import React from 'react';
import {AbsoluteFill, Sequence, useCurrentFrame} from 'remotion';
import {C, F, ci, sp, inSchuif, Scene, Kop, Kaart} from './stijl';
import X from './d4.json';

export const DUUR4 = 420;
const KL = ['#00811F', '#4EB051', '#00548F', '#0E2A4D', '#2E9C8F', '#D52B1E', '#8A5A00', '#B35A9A', '#E08A00', '#6C7A80', '#7A4FB0', '#3E4B50', '#9C6B30'];
const N = X.nodes, BUREN = X.buren.filter((b, i) => N[b][1] < -100 && i !== 4 && i !== 5), LAB = Object.fromEntries(X.lab);
const naamVan = {[X.route[1]]: 'Sportlaan'};
['Stadionpark', 'Stadionweg', 'Feijenoord', 'stadsbrug', 'treinstation', 'Getijdenpark'].forEach((n, i) => {naamVan[X.buren[i]] = n;});
const E = X.e.filter((e) => e[2] > 0.3);
const mix = (a, b, t) => a + (b - a) * t;

const Verkenner = () => {
  const f = useCurrentFrame(), z = ci(f, 40, 170);
  // camera: hele web → rond Feyenoord City en Parkeren
  const cx = mix(-130, 70, z), cy = mix(30, -215, z), h = mix(1460, 470, z), w = (h * 16) / 9;
  const rs = h / 1080; // straal mee laten schalen, zodat punten op beeld even groot blijven
  const fc = N[X.fc], bur = ci(f, 175, 200), rt = ci(f, 225, 280);
  const pad = X.route.map((i) => N[i]);
  const lengte = pad.slice(1).reduce((s, p, i) => s + Math.hypot(p[0] - pad[i][0], p[1] - pad[i][1]), 0);
  const label = (i, d, groot) => {
    const [x, y] = N[i];
    return <text key={'l' + i} x={x} y={y - (groot ? 16 : 12) * rs} textAnchor="middle" fontSize={(groot ? 30 : 24) * rs} fontWeight={groot ? 700 : 400}
      fill={groot ? '#000' : C.sub} opacity={ci(f, d, d + 12)} style={{paintOrder: 'stroke'}} stroke={C.grijs} strokeWidth={6 * rs}>{LAB[i] || naamVan[i]}</text>;
  };
  return (
    <Scene dur={330}>
      <svg viewBox={`${cx - w / 2} ${cy - h / 2} ${w} ${h}`} width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0, opacity: ci(f, 0, 30)}}>
        {E.map(([a, b], i) => <line key={i} x1={N[a][0]} y1={N[a][1]} x2={N[b][0]} y2={N[b][1]} stroke={C.lijn} strokeWidth={0.8 * rs} opacity={0.45 * (1 - 0.6 * bur)} />)}
        {N.map(([x, y, s, n], i) => <circle key={i} cx={x} cy={y} r={(s === 'o' ? 9 : s === 'p' ? 6 : 3 + Math.min(4, Math.log10(n + 1))) * rs}
          fill={KL[X.ndom[i]] || C.sub} opacity={0.75 * (1 - 0.7 * bur)} />)}
        {BUREN.map((b) => <line key={'b' + b} x1={fc[0]} y1={fc[1]} x2={N[b][0]} y2={N[b][1]} stroke={C.groen} strokeWidth={3 * rs} opacity={bur} />)}
        <polyline points={pad.map((p) => p.slice(0, 2).join(',')).join(' ')} fill="none" stroke={C.rood} strokeWidth={6 * rs} strokeLinecap="round"
          strokeDasharray={lengte} strokeDashoffset={lengte * (1 - rt)} />
        {[...BUREN, ...X.route].map((b) => <circle key={'k' + b} cx={N[b][0]} cy={N[b][1]} r={(b === X.fc || b === X.park ? 16 : 10) * rs}
          fill={X.route.includes(b) && b !== X.fc ? C.rood : C.groen} stroke="#fff" strokeWidth={3 * rs} opacity={b === X.fc ? ci(f, 150, 165) : X.route.includes(b) ? ci(f, 225, 240) : bur} />)}
        {f < 150 && [...X.lab].sort((a, b) => N[b[0]][3] - N[a[0]][3]).slice(0, 16).filter(([i]) => i !== X.fc && i !== X.park && N[i][1] > -560).map(([i]) => label(i, 20))}
        {label(X.fc, 150, true)}
        {BUREN.map((b) => label(b, 185))}
        {label(X.route[1], 240)}
        {label(X.park, 262, true)}
      </svg>
      <div style={{position: 'absolute', left: 0, top: 0, width: 1100, height: 260, background: `radial-gradient(ellipse at 20% 30%, ${C.grijs} 55%, rgba(239,244,246,0) 75%)`}} />
      <Kop f={f} tekst="Ontdek de verbanden" sub={`De Verkenner: ${X.nodes.length.toLocaleString('nl-NL')} begrippen uit ${X.n.toLocaleString('nl-NL')} debatten en stukken`} />
      <div style={{position: 'absolute', right: 90, bottom: 80, fontSize: 30, background: '#fff', borderRadius: 14, padding: '16px 26px', boxShadow: '0 12px 40px rgba(0,40,20,.10)', ...inSchuif(f, 230, 20)}}>
        Route: <b>Feyenoord City</b> → Sportlaan → <b style={{color: C.rood}}>Parkeren</b>
      </div>
    </Scene>
  );
};

// flits van Inzichten: moties, toezeggingen en vragen per jaar
const SRT = [['Moties', C.groen], ['Toezeggingen', C.blauw], ['Schriftelijke vragen', C.mid]];
const Inzichten = () => {
  const f = useCurrentFrame(), max = Math.max(...X.ins.map((r) => r[1] + r[2] + r[3]));
  return (
    <Scene dur={90}>
      <Kop f={f} tekst="En in Inzichten: de cijfers" sub="Moties, toezeggingen en schriftelijke vragen per jaar" />
      <Kaart style={{left: 90, top: 270, width: 1740, height: 740, padding: '40px 60px'}}>
        <div style={{display: 'flex', gap: 30, fontSize: 26}}>{SRT.map(([n, k]) => <span key={n}><span style={{display: 'inline-block', width: 22, height: 22, background: k, borderRadius: 4, verticalAlign: -3, marginRight: 8}} />{n}</span>)}</div>
        <div style={{position: 'absolute', left: 60, right: 60, bottom: 70, height: 520, display: 'flex', alignItems: 'flex-end', gap: 40}}>
          {X.ins.map(([j, ...v], i) => {
            const g = sp(f, 6 + i * 3, {damping: 18, stiffness: 110});
            return (
              <div key={j} style={{flex: 1, display: 'flex', flexDirection: 'column-reverse', height: '100%', position: 'relative'}}>
                {v.map((n, s) => <div key={s} style={{height: `${(n / max) * 100 * g}%`, background: SRT[s][1], borderRadius: s === 2 ? '6px 6px 0 0' : 0}} />)}
                <div style={{position: 'absolute', bottom: -46, left: 0, right: 0, textAlign: 'center', fontSize: 24, color: C.sub}}>{j}</div>
              </div>
            );
          })}
        </div>
      </Kaart>
    </Scene>
  );
};

export const Deel4 = () => (
  <AbsoluteFill style={{background: C.grijs, fontFamily: F}}>
    <Sequence from={0} durationInFrames={330}><Verkenner /></Sequence>
    <Sequence from={330} durationInFrames={90}><Inzichten /></Sequence>
  </AbsoluteFill>
);
