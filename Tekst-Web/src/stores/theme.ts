import type { GlobalThemeOverrides } from 'naive-ui';
import _mergeWith from 'lodash.mergewith';
import Color from 'color';
import { computed, ref, watch } from 'vue';
import { useStateStore } from '@/stores';
import { lightTheme, darkTheme } from 'naive-ui';
import { usePreferredDark } from '@vueuse/core';
import { defineStore } from 'pinia';
import { usePlatformData } from '@/composables/platformData';

export declare type ThemeMode = 'light' | 'dark';

const commonOverrides: GlobalThemeOverrides = {
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

const lightOverrides: GlobalThemeOverrides = {
  common: {
    bodyColor: '#ffffff',
  },
};

const darkOverrides: GlobalThemeOverrides = {
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

_mergeWith(lightOverrides, commonOverrides);
_mergeWith(darkOverrides, commonOverrides);

export const useThemeStore = defineStore('theme', () => {
  const state = useStateStore();
  const { pfData } = usePlatformData();
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

  function generateAccentColorVariants(
    baseColor: string = state.text?.accentColor || '#7A7A7A',
    dark: boolean = darkMode.value
  ) {
    const lighten = dark ? 0.8 : 0.0;
    const baseStatic = Color(baseColor);
    const base = baseStatic.lighten(lighten);
    return {
      base: base.hex(),
      fade1: base.fade(0.2).hexa(),
      fade2: base.fade(0.4).hexa(),
      fade3: base.fade(0.6).hexa(),
      fade4: base.fade(0.8).hexa(),
      fade5: base.fade(0.9).hexa(),
      dark: baseStatic.darken(0.6).hex(),
      pastel: baseStatic.saturate(0.9).lighten(1.4).hex(),
    };
  }

  // all texts access color variants
  const allAccentColors = computed(() =>
    Object.fromEntries(
      pfData.value?.texts.map((t) => [
        t.id,
        generateAccentColorVariants(t.accentColor || '#7A7A7A', darkMode.value),
      ]) || []
    )
  );

  function getAccentColors(textId?: string) {
    return allAccentColors.value[textId || ''] || generateAccentColorVariants('#7A7A7A');
  }

  // current text accent color variants
  const accentColors = computed(
    () =>
      allAccentColors.value[state.text?.id || ''] ||
      generateAccentColorVariants('#7A7A7A', darkMode.value)
  );

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
    browserDarkThemePreferred,
    theme,
    overrides,
    mainBgColor,
    contentBgColor,
    generateAccentColorVariants,
    getAccentColors,
    accentColors,
  };
});
