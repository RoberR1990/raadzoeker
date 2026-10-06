// Promovideo v4 compleet: deel 1, 2, 3 en het slot (Verkenner en Inzichten weggelaten, besluit Robert: vertroebelt de kernboodschap).
import React from 'react';
import {AbsoluteFill, Series, Sequence, Audio, staticFile} from 'remotion';
import {C} from './stijl';
import {Deel1, DUUR1} from './Deel1';
import {Deel2, DUUR2} from './Deel2';
import {Deel3, DUUR3} from './Deel3';
import {Deel5, DUUR5} from './Deel5';

// voice-over (ElevenLabs, stem h6uBOiAjLKklte8hdYio): startframe per fragment, zie ontwerp/voiceover.txt
const VO = [30, 205, 340, 560, 780, 945, 1320, 1580, 1715, 1925, 2102, 2430];
const VOLEN = [4.99, 3.47, 6.43, 6.19, 4.6, 11.96, 8.12, 3.87, 6.27, 4.83, 10.11, 3.32]; // seconden
export const DUURV = DUUR1 + DUUR2 + DUUR3 + DUUR5;
export const Volledig = () => (
  <AbsoluteFill style={{background: C.grijs}}>
    <Series>
      <Series.Sequence durationInFrames={DUUR1}><Deel1 /></Series.Sequence>
      <Series.Sequence durationInFrames={DUUR2}><Deel2 /></Series.Sequence>
      <Series.Sequence durationInFrames={DUUR3}><Deel3 /></Series.Sequence>
      <Series.Sequence durationInFrames={DUUR5}><Deel5 /></Series.Sequence>
    </Series>
    <Audio src={staticFile('muziek.mp3')} volume={(f) => {
      // zacht onder de stem, iets voller in de pauzes; in- en uitfaden
      const praat = VO.some((s, i) => f >= s - 6 && f < s + VOLEN[i] * 30 + 6);
      return (praat ? 0.07 : 0.16) * Math.min(1, f / 30, (DUURV - f) / 75);
    }} />
    {VO.map((s, i) => <Sequence key={i} from={s}><Audio src={staticFile(`vo/vo${String(i + 1).padStart(2, '0')}.mp3`)} /></Sequence>)}
  </AbsoluteFill>
);
