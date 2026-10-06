// Promovideo v4, deel 3 (15 s): pagina's. Domeinen → onderwerp Parkeren (kern, volgen, net besproken, beloftespoor)
// → Gebieden: Delfshaven met besluiten van de wijkraden. Echte data uit de site (src/d3.json).
import React from 'react';
import {AbsoluteFill, Sequence, useCurrentFrame} from 'remotion';
import {C, F, ci, sp, inSchuif, Scene, Kop, Kaart, Cursor} from './stijl';
import X from './d3.json';

export const DUUR3 = 460;
const MND = ['jan', 'feb', 'mrt', 'apr', 'mei', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov', 'dec'];
const dat = (s) => `${+s.slice(8, 10)} ${MND[+s.slice(5, 7) - 1]} ${s.slice(0, 4)}`;
const punten = (d) => (d.match(/-?\d+(\.\d+)?/g) || []).map(Number);
const kader = (ds) => {
  let a = [1e9, 1e9, -1e9, -1e9];
  ds.forEach((d) => {const p = punten(d); for (let i = 0; i + 1 < p.length; i += 2) {a = [Math.min(a[0], p[i]), Math.min(a[1], p[i + 1]), Math.max(a[2], p[i]), Math.max(a[3], p[i + 1])];}});
  return a;
};
const Badge = ({kl, children, style}) => <span style={{fontSize: 19, fontWeight: 700, color: '#fff', background: kl, borderRadius: 999, padding: '4px 13px', ...style}}>{children}</span>;

// 1. dossierkast met de 13 domeinen; klik op Mobiliteit
const Domeinen = () => {
  const f = useCurrentFrame(), klik = 62, mi = X.dom.indexOf('Mobiliteit');
  return (
    <Scene dur={110}>
      <Kop f={f} tekst="Elk domein, onderwerp en gebied" sub="Een eigen pagina, met wat er is gezegd, besloten en beloofd" />
      {X.dom.map((n, i) => {
        const col = i % 5, rij = Math.floor(i / 5), aan = i === mi && f >= klik;
        return (
          <Kaart key={n} style={{left: 90 + col * 352, top: 330 + rij * 210, width: 330, height: 180, padding: '28px 30px', ...inSchuif(f, 8 + i * 3, 30),
            background: aan ? C.groen : '#fff', color: aan ? '#fff' : '#000', borderLeft: `8px solid ${aan ? C.groenD : C.groen}`}}>
            <div style={{fontSize: 32, fontWeight: 700, lineHeight: 1.15}}>{n}</div>
            <div style={{fontSize: 21, marginTop: 10, color: aan ? '#fff' : C.sub}}>{i === mi ? 'Parkeren · OV · fiets · verkeer' : 'domein'}</div>
          </Kaart>
        );
      })}
      <Cursor f={f} klik={klik} x={ci(f, 20, klik, 1500, 90 + (mi % 5) * 352 + 200)} y={ci(f, 20, klik, 950, 330 + Math.floor(mi / 5) * 210 + 110)} />
    </Scene>
  );
};

// 2. onderwerpspagina Parkeren
const SPOOR = [
  ['Toezegging', 'Kader betaald parkeren – parkeerdrukmetingen', 'wethouder Zeegers · 23 sep 2026', 'Afdoening verwacht', C.blauw],
  ['Motie', 'Geen parkeeroverlast omwonenden RTHA', 'Leefbaar Rotterdam · aangenomen 39–4', 'Loopt nog', '#8A5A00'],
  ['Toezegging', 'Aarhof Imkerstraat – parkeerberekening', 'wethouder Lansink-Bastemeijer · 3 jun 2026', 'Afgedaan', C.groen],
];
const Parkeren = () => {
  const f = useCurrentFrame(), klik = 70, volg = f >= klik;
  return (
    <Scene dur={170}>
      <div>
        <div style={{position: 'absolute', left: 90, top: 58, fontSize: 26, color: C.sub, ...inSchuif(f, 0, 20)}}>Domeinen › Mobiliteit › <b style={{color: '#000'}}>Parkeren</b></div>
        <div style={{position: 'absolute', left: 90, top: 100, fontSize: 76, fontWeight: 700, ...inSchuif(f, 4, 24)}}>Parkeren</div>
        <div style={{position: 'absolute', left: 90, top: 200, width: 1100, fontSize: 32, lineHeight: 1.35, ...inSchuif(f, 12, 20)}}>{X.kern}</div>
        <div style={{position: 'absolute', left: 1430, top: 112, fontSize: 30, fontWeight: 700, borderRadius: 999, padding: '16px 30px', border: `3px solid ${C.groen}`,
          background: volg ? C.groen : '#fff', color: volg ? '#fff' : C.groen, transform: `scale(${volg ? 0.94 + 0.06 * sp(f, klik) : 1})`, ...inSchuif(f, 16, 20)}}>
          {volg ? '★ Je volgt dit' : '☆ Volg dit onderwerp'}
        </div>
        <div style={{position: 'absolute', left: 1330, top: 200, width: 500, fontSize: 24, background: C.navy, color: '#fff', borderRadius: 14, padding: '14px 22px',
          opacity: Math.min(ci(f, klik + 6, klik + 14), ci(f, klik + 60, klik + 72, 1, 0)), transform: `translateY(${ci(f, klik + 6, klik + 16, -10, 0)}px)`}}>
          Je krijgt een seintje als er iets nieuws is
        </div>
        <Kaart style={{left: 90, top: 340, width: 760, height: 640, ...inSchuif(f, 26, 40)}}>
          <div style={{fontSize: 34, fontWeight: 700, marginBottom: 18}}>Net besproken</div>
          {X.net.map(([, nr, titel, datum, verg], i) => (
            <div key={i} style={{borderTop: `2px solid ${C.grijs2}`, padding: '16px 0', ...inSchuif(f, 34 + i * 8, 16)}}>
              <div style={{fontSize: 21, color: C.sub}}>{verg} · {dat(datum)}</div>
              <div style={{fontSize: 28, fontWeight: 700, color: C.groenD, marginTop: 4}}>{titel} <span style={{fontWeight: 400, color: C.groen}}>▶</span></div>
            </div>
          ))}
        </Kaart>
        <Kaart style={{left: 890, top: 340, width: 940, height: 640, ...inSchuif(f, 40, 40)}}>
          <div style={{fontSize: 34, fontWeight: 700, marginBottom: 18}}>Beloofd en besloten</div>
          {SPOOR.map(([soort, titel, wie, stand, kl], i) => (
            <div key={i} style={{borderTop: `2px solid ${C.grijs2}`, padding: '18px 0', ...inSchuif(f, 90 + i * 12, 16)}}>
              <Badge kl={C.sub}>{soort}</Badge>
              <Badge kl={kl} style={{marginLeft: 10, opacity: ci(f, 104 + i * 12, 112 + i * 12), transform: `scale(${sp(f, 104 + i * 12)})`, display: 'inline-block'}}>{stand}</Badge>
              <div style={{fontSize: 29, fontWeight: 700, marginTop: 10}}>{titel}</div>
              <div style={{fontSize: 22, color: C.sub, marginTop: 4}}>{wie}</div>
            </div>
          ))}
        </Kaart>
        <Cursor f={f} klik={klik} x={ci(f, 30, klik, 1200, 1580) + ci(f, klik + 18, klik + 40, 0, 160)} y={ci(f, 30, klik, 700, 150) + ci(f, klik + 18, klik + 40, 0, 260)} />
      </div>
    </Scene>
  );
};

// 3. gebieden: klik op Delfshaven → wat er speelt en besluiten van de wijkraden
const BESLUIT = [
  ['Wijkraad Delfshaven-Schiemond', '21 jul 2026', 'Bewonersinitiatief Pottentuin goedgekeurd', '5 stemmen voor, 1 tegen'],
  ['Wijkraad Middelland-Nieuwe Westen', '3 sep 2026', 'Summerschool en zomerfeest', 'unaniem akkoord'],
  ['Wijkraad Bospolder-Spangen-Tussendijken', '26 mei 2026', 'Ingesproken bij de raadscommissie over tram 4', 'busverbinding op marktdagen wordt bekeken'],
  ['Wijkraad Middelland-Nieuwe Westen', '4 feb 2026', 'Hondenlosloopgebied Heemraadssingel', 'wil alsnog in gesprek'],
];
const DH = X.geb.find((g) => g[0] === 'Delfshaven');
const GK = kader(X.geb.map((g) => g[1]));
const Gebieden = () => {
  const f = useCurrentFrame(), klik = 48, [dx0, dy0, dx1, dy1] = kader([DH[1]]);
  const [x0, y0, x1, y1] = GK, schaal = 1500 / (x1 - x0), z = ci(f, klik + 6, klik + 40);
  const cx = (dx0 + dx1) / 2, cy = (dy0 + dy1) / 2;
  // inzoomen op Delfshaven: viewBox schuift van de hele stad naar het gebied
  const vb = [x0 + (cx - 90 - x0) * z, y0 + (cy - 80 - y0) * z, (x1 - x0) * (1 - z) + 180 * z, (y1 - y0) * (1 - z) + 160 * z];
  const kx = 90 + (cx - x0) * schaal, ky = 280 + (cy - y0) * schaal;
  return (
    <Scene dur={180}>
      <Kop f={f} tekst="En wat speelt er in jouw wijk?" sub="Van de gemeenteraad tot de besluiten van de wijkraad" />
      <svg viewBox={vb.join(' ')} width={ci(f, klik + 6, klik + 40, 1500, 760)} height={ci(f, klik + 6, klik + 40, (1500 * (y1 - y0)) / (x1 - x0), 676)} style={{position: 'absolute', left: 90, top: 280, background: '#fff', borderRadius: 18, boxShadow: '0 12px 40px rgba(0,40,20,.10)'}}>
        <path d={X.water} fill="#CFE3EE" />
        {X.geb.map(([n, d]) => <path key={n} d={d} fill={n === 'Delfshaven' && f >= klik ? C.groen : C.zacht} stroke="#fff" strokeWidth={z > 0.5 ? 0.6 : 1.2} />)}
      </svg>
      {f < klik + 6 && <Cursor f={f} klik={klik} x={ci(f, 10, klik, 1300, kx)} y={ci(f, 10, klik, 950, ky)} />}
      <div style={{position: 'absolute', left: 900, top: 280, width: 930, opacity: ci(f, klik + 24, klik + 36), transform: `translateX(${ci(f, klik + 24, klik + 40, 60, 0)}px)`}}>
        <div style={{fontSize: 64, fontWeight: 700}}>Delfshaven</div>
        <div style={{fontSize: 27, lineHeight: 1.4, margin: '12px 0 26px', color: C.sub}}>{X.dhkern}</div>
        <div style={{fontSize: 32, fontWeight: 700, marginBottom: 10}}>Besluiten van de wijkraden</div>
        {BESLUIT.map(([raad, d, t, uit], i) => (
          <div key={i} style={{background: '#fff', borderRadius: 14, padding: '14px 22px', marginBottom: 12, boxShadow: '0 8px 24px rgba(0,40,20,.08)', ...inSchuif(f, klik + 50 + i * 10, 20)}}>
            <div style={{fontSize: 20, color: C.sub}}>{raad} · {d}</div>
            <div style={{fontSize: 26, fontWeight: 700, marginTop: 2}}>{t} <span style={{fontWeight: 400, color: C.groen}}>· {uit}</span></div>
          </div>
        ))}
      </div>
    </Scene>
  );
};

export const Deel3 = () => (
  <AbsoluteFill style={{background: C.grijs, fontFamily: F}}>
    <Sequence from={0} durationInFrames={110}><Domeinen /></Sequence>
    <Sequence from={110} durationInFrames={170}><Parkeren /></Sequence>
    <Sequence from={280} durationInFrames={180}><Gebieden /></Sequence>
  </AbsoluteFill>
);
