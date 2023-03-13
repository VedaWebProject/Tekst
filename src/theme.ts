import type { GlobalThemeOverrides } from 'naive-ui';
import _merge from 'lodash.merge';

export declare type ThemeMode = 'light' | 'dark';

const commonOverrides: GlobalThemeOverrides = {
  common: {
    fontSize: '18px',
    fontSizeMini: '16px',
    fontSizeTiny: '16px',
    fontSizeSmall: '18px',
    fontSizeMedium: '18px',
    fontSizeLarge: '20px',
    fontSizeHuge: '22px',
    lineHeight: '1.8',
    fontFamily: 'var(--app-ui-font-family)',
    fontWeight: 'var(--app-ui-font-weight)',
  },
  Form: {
    feedbackPadding: '4px 0 8px 2px',
    feedbackHeightSmall: '18px',
    feedbackHeightMedium: '18px',
    feedbackHeightLarge: '20px',
  },
};

const lightOverrides: GlobalThemeOverrides = {
  common: {
    bodyColor: '#ffffff',
    primaryColor: '#7d7d7d',
    primaryColorHover: '#8e8e8e',
    primaryColorPressed: '#8e8e8e',
    primaryColorSuppl: '#8e8e8e',
  },
};

const darkOverrides: GlobalThemeOverrides = {
  common: {
    bodyColor: '#232323',
    primaryColor: '#b6b6b6',
    primaryColorHover: '#c9c9c9',
    primaryColorPressed: '#c9c9c9',
    primaryColorSuppl: '#c9c9c9',
  },
  Card: {
    colorEmbedded: '#2a2a2a',
  },
};

_merge(lightOverrides, commonOverrides);
_merge(darkOverrides, commonOverrides);

export { lightOverrides, darkOverrides };
