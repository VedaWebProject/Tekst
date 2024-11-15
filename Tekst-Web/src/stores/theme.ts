import { usePlatformData } from '@/composables/platformData';
import { useStateStore } from '@/stores';
import { usePreferredDark } from '@vueuse/core';
import { adjustHue, lighten, saturate, toRgba, transparentize } from 'color2k';
import { mergeWith } from 'lodash-es';
import type { GlobalThemeOverrides } from 'naive-ui';
import { darkTheme, lightTheme } from 'naive-ui';
import { defineStore } from 'pinia';
import { computed, ref, watch } from 'vue';

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

mergeWith(lightOverrides, commonOverrides);
mergeWith(darkOverrides, commonOverrides);

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
  const messageBgColor = computed(() => (darkMode.value ? '#232323' : '#ffffff'));

  function generateAccentColorVariants(
    baseColor: string = state.text?.accentColor || '#7A7A7A',
    dark: boolean = darkMode.value
  ) {
    const lightenBy = dark ? 0.375 : 0.0;
    const baseStatic = baseColor;
    const base = lighten(baseColor, lightenBy);
    return {
      base: toRgba(base),
      fade1: toRgba(transparentize(base, 0.2)),
      fade2: toRgba(transparentize(base, 0.4)),
      fade3: toRgba(transparentize(base, 0.6)),
      fade4: toRgba(transparentize(base, 0.8)),
      fade5: toRgba(transparentize(base, 0.9)),
      // this is supposed to create an attention-grabbing UI highlight color that
      // complements each text's accent color
      spotlight: toRgba(lighten(adjustHue(saturate(baseStatic, 0.3), 180), 0.45)),
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
    const primary = toRgba(accentColors.value.base);
    const baseOverrides = darkMode.value ? darkOverrides : lightOverrides;
    return {
      ...baseOverrides,
      common: {
        ...baseOverrides.common,
        primaryColor: primary,
        primaryColorHover: toRgba(lighten(primary, 0.075)),
        primaryColorPressed: toRgba(saturate(lighten(primary, 0.2), 0.1)),
        primaryColorSuppl: primary,
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
    messageBgColor,
    generateAccentColorVariants,
    getAccentColors,
    accentColors,
  };
});
