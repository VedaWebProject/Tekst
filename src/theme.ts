import type { GlobalThemeOverrides } from 'naive-ui';
import extend from 'just-extend';

const commonOverrides: GlobalThemeOverrides = {
  common: {
    // warningColor: '#00ff00',
  },
};

const lightOverrides: GlobalThemeOverrides = {
  common: {
    bodyColor: '#FFFFFF',
  },
};

const darkOverrides: GlobalThemeOverrides = {
  common: {
    bodyColor: '#262626',
  },
};

extend(true, lightOverrides, commonOverrides);
extend(true, darkOverrides, commonOverrides);

export { lightOverrides, darkOverrides };
