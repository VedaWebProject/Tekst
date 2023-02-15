import type { GlobalThemeOverrides } from 'naive-ui';
import _merge from 'lodash.merge';

const commonOverrides: GlobalThemeOverrides = {
  common: {
    fontSize: '16px',
    fontSizeMini: '14px',
    fontSizeTiny: '14px',
    fontSizeSmall: '16px',
    fontSizeMedium: '16px',
    fontSizeLarge: '17px',
    fontSizeHuge: '18px',
    lineHeight: '1.8',
  },
};

const lightOverrides: GlobalThemeOverrides = {
  common: {
    bodyColor: '#FFFFFF',
  },
};

const darkOverrides: GlobalThemeOverrides = {
  common: {
    bodyColor: '#181818',
  },
};

_merge(lightOverrides, commonOverrides);
_merge(darkOverrides, commonOverrides);

export { lightOverrides, darkOverrides };
