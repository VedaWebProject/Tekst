import type { GlobalThemeOverrides } from 'naive-ui';
import _merge from 'lodash.merge';
import Color from 'color';
import { computed } from 'vue';
import { useStateStore } from '@/stores';
import { lightTheme, darkTheme } from 'naive-ui';

export declare type ThemeMode = 'light' | 'dark';

const commonOverrides: GlobalThemeOverrides = {
  common: {
    fontFamily: 'var(--app-ui-font-family)',
    fontWeight: 'var(--app-ui-font-weight-light)',
    fontSize: 'var(--app-ui-font-size)',
    fontSizeMini: 'var(--app-ui-font-size-mini)',
    fontSizeTiny: 'var(--app-ui-font-size-tiny)',
    fontSizeSmall: 'var(--app-ui-font-size-small)',
    fontSizeMedium: 'var(--app-ui-font-size-medium)',
    fontSizeLarge: 'var(--app-ui-font-size-large)',
    fontSizeHuge: 'var(--app-ui-font-size-huge)',
  },
  Form: {
    feedbackPadding: '4px 0 8px 2px',
    feedbackHeightSmall: '18px',
    feedbackHeightMedium: '18px',
    feedbackHeightLarge: '20px',
  },
  Badge: {
    fontSize: 'var(--app-ui-font-size-mini)',
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
  },
  Card: {
    colorEmbedded: '#2a2a2a',
  },
};

_merge(lightOverrides, commonOverrides);
_merge(darkOverrides, commonOverrides);

export function useTheme() {
  const state = useStateStore();
  const theme = computed(() => (state.themeMode === 'light' ? lightTheme : darkTheme));
  const mainBgColor = computed(() => (state.themeMode === 'light' ? '#00000010' : '#ffffff10'));
  const contentBgColor = computed(() => (state.themeMode === 'light' ? '#ffffffcc' : '#00000044'));

  // current text accent color variants
  const accentColors = computed(() => {
    const lighten = state.themeMode === 'dark' ? 0.25 : 0.0;
    const base = Color(state.text ? state.text.accentColor : '#18A058').lighten(lighten);
    return {
      base: base.hex(),
      fade1: base.fade(0.2).hexa(),
      fade2: base.fade(0.4).hexa(),
      fade3: base.fade(0.6).hexa(),
      fade4: base.fade(0.8).hexa(),
      fade5: base.fade(0.9).hexa(),
      inverted: base.negate().hex(),
      invertedPastel: base.negate().desaturate(0.2).lighten(0.3).hex(),
      invertedDark: base.negate().darken(0.6).hex(),
    };
  });

  const themeOverrides = computed(() => {
    const mode = state.themeMode;
    const primaryColorHex = accentColors.value.base;
    const baseOverrides = mode === 'light' ? lightOverrides : darkOverrides;
    const primaryColor = Color(primaryColorHex);
    return {
      ...baseOverrides,
      common: {
        ...baseOverrides.common,
        primaryColor: primaryColorHex,
        primaryColorHover: primaryColor.lighten(0.1).saturate(0.15).hex(),
        primaryColorPressed: primaryColor.lighten(0.3).hex(),
        primaryColorSuppl: primaryColorHex,
      },
    };
  });

  return {
    theme,
    themeOverrides,
    mainBgColor,
    contentBgColor,
    accentColors,
  };
}
