import type { GlobalThemeOverrides } from 'naive-ui';
import _mergeWith from 'lodash.mergewith';
import Color from 'color';
import { computed, ref, watch } from 'vue';
import { useStateStore } from '@/stores';
import { lightTheme, darkTheme } from 'naive-ui';
import { usePreferredDark } from '@vueuse/core';
import { defineStore } from 'pinia';

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

_mergeWith(lightOverrides, commonOverrides);
_mergeWith(darkOverrides, commonOverrides);

export const useThemeStore = defineStore('theme', () => {
  const state = useStateStore();
  const browserDarkThemePreferred = usePreferredDark();
  const darkMode = ref<boolean>(
    (localStorage.getItem('theme') as ThemeMode) === 'dark' ||
      browserDarkThemePreferred.value ||
      false
  );
  watch(darkMode, (after) => localStorage.setItem('theme', after === true ? 'dark' : 'light'));
  const toggleThemeMode = () => (darkMode.value = !darkMode.value);
  const theme = computed(() => (darkMode.value ? darkTheme : lightTheme));
  const mainBgColor = computed(() => (darkMode.value ? '#ffffff10' : '#00000010'));
  const contentBgColor = computed(() => (darkMode.value ? '#00000044' : '#ffffffcc'));

  // current text accent color variants
  const accentColors = computed(() => {
    const lighten = darkMode.value ? 0.25 : 0.0;
    const baseStatic = Color(state.text ? state.text.accentColor : '#7A7A7A');
    const base = baseStatic.lighten(lighten);
    const inverted = baseStatic.negate().darken(0.1);
    return {
      base: base.hex(),
      fade1: base.fade(0.2).hexa(),
      fade2: base.fade(0.4).hexa(),
      fade3: base.fade(0.6).hexa(),
      fade4: base.fade(0.8).hexa(),
      fade5: base.fade(0.9).hexa(),
      inverted: inverted.hex(),
      invertedPastel: inverted.saturate(0.9).lighten(0.5).hex(),
      invertedDark: inverted.darken(0.75).hex(),
    };
  });

  const overrides = computed(() => {
    const primaryColorHex = accentColors.value.base;
    const baseOverrides = darkMode.value ? darkOverrides : lightOverrides;
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
    darkMode,
    toggleThemeMode,
    theme,
    overrides,
    mainBgColor,
    contentBgColor,
    accentColors,
  };
});
