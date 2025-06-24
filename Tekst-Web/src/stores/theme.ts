import { useStateStore } from '@/stores';
import { usePreferredDark, useSessionStorage } from '@vueuse/core';
import { lighten, saturate, toRgba, transparentize } from 'color2k';
import type { GlobalThemeOverrides } from 'naive-ui';
import { darkTheme, lightTheme } from 'naive-ui';
import { defineStore } from 'pinia';
import { computed, watchEffect } from 'vue';

const _COMMON_OVERRIDES: GlobalThemeOverrides = {
  common: {
    fontFamily: 'var(--font-family-ui)',
    fontWeight: 'normal',
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
    labelFontWeight: 'bold',
  },
  Badge: {
    fontSize: 'var(--font-size-mini)',
    color: '#cc3d39',
  },
  Thing: {
    titleFontWeight: 'normal',
    fontSize: 'var(--font-size)',
  },
  Tabs: {
    tabFontSizeSmall: 'var(--font-size-small)',
    tabFontSizeMedium: 'var(--font-size-medium)',
    tabFontSizeLarge: 'var(--font-size-large)',
  },
  Alert: {
    fontSize: 'var(--font-size-medium)',
    titleFontWeight: 'bold',
  },
  Table: {
    thFontWeight: 'bold',
  },
  Empty: {
    textColor: 'var(--text-color-translucent)',
    iconColor: 'var(--text-color-translucent)',
  },
};

const _LIGHT_OVERRIDES: GlobalThemeOverrides = {
  ..._COMMON_OVERRIDES,
  common: {
    ..._COMMON_OVERRIDES.common,
    bodyColor: '#FFFFFF',
  },
};

const _DARK_OVERRIDES: GlobalThemeOverrides = {
  ..._COMMON_OVERRIDES,
  common: {
    ..._COMMON_OVERRIDES.common,
    bodyColor: '#232323',
  },
  Button: {
    ..._COMMON_OVERRIDES.Button,
    textColorPrimary: '#232323FF',
  },
  Card: {
    ..._COMMON_OVERRIDES.Card,
    colorEmbedded: '#2a2a2a',
  },
};

export declare type ThemeMode = 'light' | 'dark';

export const useThemeStore = defineStore('theme', () => {
  const state = useStateStore();
  const dark = useSessionStorage<boolean>('darkMode', usePreferredDark().value);
  const toggleThemeMode = () => (dark.value = !dark.value);

  function getColorShades(
    baseColor: string = state.text?.color || '#7A7A7A',
    darkMode: boolean = dark.value
  ) {
    const lightenBy = darkMode ? 0.4 : 0.0;
    const base = lighten(baseColor, lightenBy);
    return {
      base: toRgba(base),
      fade1: toRgba(transparentize(base, 0.2)),
      fade2: toRgba(transparentize(base, 0.4)),
      fade3: toRgba(transparentize(base, 0.6)),
      fade4: toRgba(transparentize(base, 0.8)),
      fade5: toRgba(transparentize(base, 0.9)),
    };
  }

  // all texts color variants
  const _allTextColors = computed(() =>
    Object.fromEntries(
      state.pf?.texts.map((t) => [t.id, getColorShades(t.color || '#7A7A7A', dark.value)]) || []
    )
  );

  function getTextColors(textId?: string | null) {
    return _allTextColors.value[textId || ''] || getColorShades('#7A7A7A', dark.value);
  }

  const colors = computed(() => ({
    mainBg: dark.value ? '#ffffff10' : '#00000010',
    contentBg: dark.value ? '#0004' : '#fff',
    primary: getColorShades(state.pf?.state.uiColor || '#305D97', dark.value),
    text: getTextColors(state.text?.id),
  }));

  const nuiBaseTheme = computed(() => (dark.value ? darkTheme : lightTheme));

  const nuiThemeOverrides = computed(() => {
    const primary = toRgba(colors.value.primary.base);
    const baseOverrides = dark.value ? _DARK_OVERRIDES : _LIGHT_OVERRIDES;
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

  // set/update global CSS vars for use in CSS contexts
  watchEffect(() => {
    Object.entries({
      '--primary-color': colors.value.primary.base,
      '--primary-color-fade1': colors.value.primary.fade1,
      '--primary-color-fade2': colors.value.primary.fade2,
      '--primary-color-fade3': colors.value.primary.fade3,
      '--primary-color-fade4': colors.value.primary.fade4,
      '--primary-color-fade5': colors.value.primary.fade5,
      '--working-text-color': colors.value.text.base,

      '--base-color': dark.value ? '#242424' : '#FFFFFF',
      '--base-color-translucent': transparentize(dark.value ? '#242424' : '#FFFFFF', 0.3),
      '--text-color': nuiBaseTheme.value.common.textColor1,
      '--text-color-translucent': transparentize(nuiBaseTheme.value.common.textColor1, 0.6),

      '--success-color': nuiBaseTheme.value.common.successColor,
      '--info-color': nuiBaseTheme.value.common.infoColor,
      '--warning-color': nuiBaseTheme.value.common.warningColor,
      '--error-color': nuiBaseTheme.value.common.errorColor,

      '--main-bg-color': colors.value.mainBg,
      '--content-bg-color': colors.value.contentBg,

      '--font-family-ui': [state.pf?.state.uiFont, `'Tekst UI Font'`, 'sans-serif']
        .filter((f) => !!f)
        .join(', '),
      '--font-family-content': [state.pf?.state.contentFont, `'Tekst Content Font'`, 'serif']
        .filter((f) => !!f)
        .join(', '),
    }).forEach(([k, v]) => {
      document.documentElement.style.setProperty(k, v);
    });
  });

  return {
    dark,
    toggleThemeMode,
    nuiBaseTheme,
    nuiThemeOverrides,
    colors,
    getTextColors,
  };
});
