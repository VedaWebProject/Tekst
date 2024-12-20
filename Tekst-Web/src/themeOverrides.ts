import { mergeWith } from 'lodash-es';
import type { GlobalThemeOverrides } from 'naive-ui';

export const commonOverrides: GlobalThemeOverrides = {
  common: {
    fontFamily: 'var(--font-family-ui)',
    fontWeight: 'var(--font-weight-normal)',
    fontSize: 'var(--font-size)',
    fontSizeMini: 'var(--font-size-mini)',
    fontSizeTiny: 'var(--font-size-tiny)',
    fontSizeSmall: 'var(--font-size-small)',
    fontSizeMedium: 'var(--font-size-medium)',
    fontSizeLarge: 'var(--font-size-large)',
    fontSizeHuge: 'var(--font-size-huge)',
  },
  Form: {
    feedbackPadding: '4px 0 8px 2px',
    feedbackHeightSmall: '18px',
    feedbackHeightMedium: '18px',
    feedbackHeightLarge: '20px',
    labelFontWeight: 'var(--font-weight-bold)',
  },
  Badge: {
    fontSize: 'var(--font-size-mini)',
  },
  Thing: {
    titleFontWeight: 'var(--font-weight-bold)',
  },
};

export const lightOverrides: GlobalThemeOverrides = {
  common: {
    bodyColor: '#ffffff',
  },
};

export const darkOverrides: GlobalThemeOverrides = {
  common: {
    bodyColor: '#232323',
  },
  Button: {
    textColorPrimary: '#232323FF',
  },
  Card: {
    colorEmbedded: '#2a2a2a',
  },
};

mergeWith(lightOverrides, commonOverrides);
mergeWith(darkOverrides, commonOverrides);
