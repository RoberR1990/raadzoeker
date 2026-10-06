// Promovideo v4 compleet: deel 1, 2, 3 en het slot (Verkenner en Inzichten weggelaten, besluit Robert: vertroebelt de kernboodschap).
import React from 'react';
import {AbsoluteFill, Series} from 'remotion';
import {C} from './stijl';
import {Deel1, DUUR1} from './Deel1';
import {Deel2, DUUR2} from './Deel2';
import {Deel3, DUUR3} from './Deel3';
import {Deel5, DUUR5} from './Deel5';

export const DUURV = DUUR1 + DUUR2 + DUUR3 + DUUR5;
export const Volledig = () => (
  <AbsoluteFill style={{background: C.grijs}}>
    <Series>
      <Series.Sequence durationInFrames={DUUR1}><Deel1 /></Series.Sequence>
      <Series.Sequence durationInFrames={DUUR2}><Deel2 /></Series.Sequence>
      <Series.Sequence durationInFrames={DUUR3}><Deel3 /></Series.Sequence>
      <Series.Sequence durationInFrames={DUUR5}><Deel5 /></Series.Sequence>
    </Series>
  </AbsoluteFill>
);
