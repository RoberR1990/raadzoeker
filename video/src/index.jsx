import React from 'react';
import {registerRoot, Composition} from 'remotion';
import {Promo, DUUR} from './Promo';
import {Deel1, DUUR1} from './Deel1';
import {Deel2, DUUR2} from './Deel2';

const Root = () => (
  <>
    <Composition id="Promo" component={Promo} durationInFrames={DUUR} fps={30} width={1920} height={1080} />
    <Composition id="Deel2" component={Deel2} durationInFrames={DUUR2} fps={30} width={1920} height={1080} />
    <Composition id="Deel1" component={Deel1} durationInFrames={DUUR1} fps={30} width={1920} height={1080} />
  </>
);
registerRoot(Root);
