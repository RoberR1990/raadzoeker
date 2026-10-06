// Promovideo v4, deel 4 (14 s): bonus. De Verkenner (kennisgraaf van alles wat gezegd en geschreven is): rustig inzoomen op
// 'Feyenoord City en stadion', buren lichten op, route naar 'Parkeren'. Daarna een flits van Inzichten. Echte data (src/d4.json).
import React from 'react';
import {AbsoluteFill, Sequence, useCurrentFrame} from 'remotion';
import {C, F, ci, sp, inSchuif, Scene, Kop, Kaart} from './stijl';
import X from './d4.json';

export const DUUR4 = 630;
const KL = ['#00811F', '#4EB051', '#00548F', '#0E2A4D', '#2E9C8F', '#D52B1E', '#8A5A00', '#B35A9A', '#E08A00', '#6C7A80', '#7A4FB0', '#3E4B50', '#9C6B30'];
const N = X.nodes, BUREN = X.buren.filter((b, i) => N[b][1] < -100 && i !== 4 && i !== 5), LAB = Object.fromEntries(X.lab);
const naamVan = {[X.route[1]]: 'Sportlaan'};
['Stadionpark', 'Stadionweg', 'Feijenoord', 'stadsbrug', 'treinstation', 'Getijdenpark'].forEach((n, i) => {naamVan[X.buren[i]] = n;});
const E = X.e.filter((e) => e[2] > 0.3);
const mix = (a, b, t) => a + (b - a) * t;

// camera zweeft langs clusters (breedte), zoomt per cluster in op begrippen (diepte) en eindigt rustig bij één verband
const STOP = [[-643, -313, 'Veiligheid'], [-690, 380, 'Werk, inkomen en armoede'], [82, 152, 'Wonen en bouwen'], [291, -396, 'Mobiliteit']];
const KAM = [[0, -130, 30, 1460], [55, -130, 30, 1460], [80, -643, -313, 560], [110, -643, -313, 500], [132, -690, 380, 560], [160, -690, 380, 500],
  [182, 82, 152, 560], [207, 82, 152, 500], [228, 291, -396, 560], [248, 291, -396, 520], [282, 70, -215, 470], [390, 70, -215, 440]];
const kam = (f) => {
  let i = 0; while (i < KAM.length - 2 && f > KAM[i + 1][0]) i++;
  const [a, b] = [KAM[i], KAM[i + 1]], t = ci(f, a[0], b[0]);
  return [mix(a[1], b[1], t), mix(a[2], b[2], t), mix(a[3], b[3], t)];
};
// per halte de 18 grootste begrippen in beeld
const LBL = STOP.map(([x, y]) => N.map((n, i) => [i, n]).filter(([, n]) => Math.abs(n[0] - x) < 380 && Math.abs(n[1] - y) < 210).sort((a, b) => b[1][3] - a[1][3]).slice(0, 18).map(([i]) => i));
const TIJD = [[80, 125], [132, 177], [182, 222], [228, 262]];

const Verkenner = () => {
  const f = useCurrentFrame(), [cx, cy, h] = kam(f), w = (h * 16) / 9, rs = h / 1080;
  const fc = N[X.fc], bur = ci(f, 290, 310), rt = ci(f, 318, 350), vol = ci(f, 262, 285);
  const pad = X.route.map((i) => N[i]);
  const lengte = pad.slice(1).reduce((s, p, i) => s + Math.hypot(p[0] - pad[i][0], p[1] - pad[i][1]), 0);
  const tekst = (key, x, y, t, o, groot, kl) => <text key={key} x={x} y={y} textAnchor="middle" fontSize={(groot ? 30 : 23) * rs} fontWeight={groot ? 700 : 400}
    fill={kl || (groot ? '#000' : C.sub)} opacity={o} style={{paintOrder: 'stroke'}} stroke={C.grijs} strokeWidth={6 * rs}>{t}</text>;
  const label = (i, d, groot) => tekst('l' + i, N[i][0], N[i][1] - (groot ? 16 : 12) * rs, X.l[i], ci(f, d, d + 12), groot);
  return (
    <Scene dur={390}>
      <svg viewBox={`${cx - w / 2} ${cy - h / 2} ${w} ${h}`} width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0, opacity: ci(f, 0, 20)}}>
        {X.e.map(([a, b], i) => <line key={i} x1={N[a][0]} y1={N[a][1]} x2={N[b][0]} y2={N[b][1]} stroke={KL[X.ndom[a]] || C.lijn} strokeWidth={0.9 * rs} opacity={0.22 * (1 - 0.7 * vol)} />)}
        {N.map(([x, y, s, n], i) => <circle key={i} cx={x} cy={y} r={(s === 'o' ? 9 : s === 'p' ? 6 : 3 + Math.min(4, Math.log10(n + 1))) * rs}
          fill={KL[X.ndom[i]] || C.sub} opacity={0.85 * (1 - 0.7 * vol)} />)}
        {X.cent.filter(([n]) => !['Financiën', 'Onderwijs', 'Cultuur en sport'].includes(n)).map(([n, x, y]) => tekst('c' + n, x, y, n, Math.min(ci(f, 12, 26), ci(f, 58, 72, 1, 0)), true, '#000'))}
        {LBL.map((ids, s) => ids.map((i, k) => tekst(`s${s}-${i}`, N[i][0], N[i][1] - 12 * rs, X.l[i], Math.min(ci(f, TIJD[s][0] - 6 + k, TIJD[s][0] + 6 + k), ci(f, TIJD[s][1] - 8, TIJD[s][1], 1, 0)), k < 3)))}
        {STOP.map(([x, y, n], s) => tekst('h' + s, x, y - 180 * rs, n, Math.min(ci(f, TIJD[s][0] - 8, TIJD[s][0] + 4), ci(f, TIJD[s][1] - 8, TIJD[s][1], 1, 0)), true, C.groenD))}
        {BUREN.map((b) => <line key={'b' + b} x1={fc[0]} y1={fc[1]} x2={N[b][0]} y2={N[b][1]} stroke={C.groen} strokeWidth={3 * rs} opacity={bur} />)}
        <polyline points={pad.map((p) => p.slice(0, 2).join(',')).join(' ')} fill="none" stroke={C.rood} strokeWidth={6 * rs} strokeLinecap="round"
          strokeDasharray={lengte} strokeDashoffset={lengte * (1 - rt)} />
        {[...BUREN, ...X.route].map((b) => <circle key={'k' + b} cx={N[b][0]} cy={N[b][1]} r={(b === X.fc || b === X.park ? 16 : 10) * rs}
          fill={X.route.includes(b) && b !== X.fc ? C.rood : C.groen} stroke="#fff" strokeWidth={3 * rs} opacity={b === X.fc ? ci(f, 272, 284) : X.route.includes(b) ? ci(f, 318, 328) : bur} />)}
        {label(X.fc, 272, true)}
        {BUREN.map((b) => label(b, 296))}
        {label(X.route[1], 330)}
        {label(X.park, 345, true)}
      </svg>
      <div style={{position: 'absolute', left: 0, top: 0, width: 1100, height: 260, background: `radial-gradient(ellipse at 20% 30%, ${C.grijs} 55%, rgba(239,244,246,0) 75%)`}} />
      <Kop f={f} tekst="Ontdek de verbanden" sub={`De Verkenner: ${X.nodes.length.toLocaleString('nl-NL')} begrippen uit ${X.n.toLocaleString('nl-NL')} debatten en stukken`} />
      <div style={{position: 'absolute', right: 90, bottom: 80, fontSize: 30, background: '#fff', borderRadius: 14, padding: '16px 26px', boxShadow: '0 12px 40px rgba(0,40,20,.10)', ...inSchuif(f, 340, 20)}}>
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

// tweede inzicht: waar speelt wat? aandeel per domein binnen elk gebied (2022-2026, stadsbrede stukken niet meegeteld)
const TINT = ['#F3F8F3', '#E1EFE2', '#D1E6CE', '#99CCA0', '#4EB051', '#00811F', '#006E32', '#004C31'];
const tint = (p) => TINT[Math.max(0, Math.min(7, Math.round((Math.min(30, p) / 30) * 7)))];
const UIT = [['Feijenoord', 0, 'wonen en bouwen'], ['Hoek van Holland', 3, 'economie en haven'], ['Pernis', 4, 'klimaat en energie']];
const Waar = () => {
  const f = useCurrentFrame(), lw = 330, cw = 100, rh = 40, x0 = 80, y0 = 150;
  return (
    <Scene dur={150}>
      <Kop f={f} tekst="Waar speelt wat?" sub="Per gebied: welk domein het meest terugkomt in moties, toezeggingen en vragen" />
      <Kaart style={{left: 90, top: 250, width: 1740, height: 740, padding: 0}}>
        {X.wdom.map((d, i) => <div key={d} style={{position: 'absolute', left: x0 + lw + cw * i + 30, top: y0 - 14, fontSize: 21, color: C.sub, whiteSpace: 'nowrap',
          transform: 'rotate(-35deg)', transformOrigin: 'left bottom', opacity: ci(f, 6, 18)}}>{d.split(/,| en /)[0]}</div>)}
        {X.waar.map(([g, , v], r) => (
          <React.Fragment key={g}>
            <div style={{position: 'absolute', left: x0, top: y0 + rh * r + 8, fontSize: 24, opacity: ci(f, 4 + r, 14 + r)}}>{g}</div>
            {v.map((p, i) => {
              const d = 10 + r * 2 + i, uit = UIT.find((u) => u[0] === g && u[1] === i), o = ci(f, d, d + 10);
              const dim = f > 78 && !uit ? ci(f, 78, 92, 1, 0.35) : 1;
              return <div key={i} style={{position: 'absolute', left: x0 + lw + cw * i + 2, top: y0 + rh * r + 2, width: cw - 4, height: rh - 4, background: tint(p), opacity: o * dim,
                fontSize: 19, color: p > 18 ? '#fff' : '#000', display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: 4,
                outline: uit && f > 78 ? `4px solid ${C.navy}` : 'none', transform: `scale(${uit ? 1 + 0.12 * sp(f, 80, {damping: 12}) * ci(f, 80, 84) : 1})`}}>{p}%</div>;
            })}
          </React.Fragment>
        ))}
      </Kaart>
      <div style={{position: 'absolute', left: 90, bottom: 40, fontSize: 28, color: C.sub, opacity: ci(f, 90, 102)}}>
        {UIT.map(([g, , d], i) => <span key={g}>{i ? ' · ' : ''}<b style={{color: '#000'}}>{g}</b>: {d}</span>)}
      </div>
    </Scene>
  );
};

export const Deel4 = () => (
  <AbsoluteFill style={{background: C.grijs, fontFamily: F}}>
    <Sequence from={0} durationInFrames={390}><Verkenner /></Sequence>
    <Sequence from={390} durationInFrames={90}><Inzichten /></Sequence>
    <Sequence from={480} durationInFrames={150}><Waar /></Sequence>
  </AbsoluteFill>
);
