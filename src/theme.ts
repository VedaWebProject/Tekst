import { type GlobalThemeOverrides, lightTheme } from 'naive-ui';
import _merge from 'lodash.merge';
import Color from 'color';

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
  },
};

const darkOverrides: GlobalThemeOverrides = {
  common: {
    bodyColor: '#232323',
    primaryColor: Color(lightTheme.common.primaryColor).lighten(0.2).hex(),
    primaryColorHover: Color(lightTheme.common.primaryColorHover).lighten(0.2).saturate(0.5).hex(),
    primaryColorPressed: Color(lightTheme.common.primaryColorPressed).lighten(0.2).hex(),
    primaryColorSuppl: Color(lightTheme.common.primaryColorSuppl).lighten(0.2).hex(),
  },
  Card: {
    colorEmbedded: '#2a2a2a',
  },
};

_merge(lightOverrides, commonOverrides);
_merge(darkOverrides, commonOverrides);

export { lightOverrides, darkOverrides };
