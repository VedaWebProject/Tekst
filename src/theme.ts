import type { GlobalThemeOverrides } from 'naive-ui';
import merge from 'lodash.merge';

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

merge(lightOverrides, commonOverrides);
merge(darkOverrides, commonOverrides);

export { lightOverrides, darkOverrides };
