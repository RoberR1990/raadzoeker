import React from 'react';
import {registerRoot, Composition} from 'remotion';
import {Promo, DUUR} from './Promo';

const Root = () => (
  <Composition id="Promo" component={Promo} durationInFrames={DUUR} fps={30} width={1920} height={1080} />
);
registerRoot(Root);
