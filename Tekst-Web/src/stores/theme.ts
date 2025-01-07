import { usePlatformData } from '@/composables/platformData';
import { useStateStore } from '@/stores';
import { usePreferredDark, useStorage } from '@vueuse/core';
import { adjustHue, lighten, saturate, toRgba, transparentize } from 'color2k';
import type { GlobalThemeOverrides } from 'naive-ui';
import { darkTheme, lightTheme } from 'naive-ui';
import { defineStore } from 'pinia';
import { computed, watchEffect } from 'vue';

const _COMMON_OVERRIDES: GlobalThemeOverrides = {
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

const _LIGHT_OVERRIDES: GlobalThemeOverrides = {
  ..._COMMON_OVERRIDES,
  common: {
    ..._COMMON_OVERRIDES.common,
    bodyColor: '#ffffff',
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
  const { pfData } = usePlatformData();
  const dark = useStorage<boolean>('darkMode', usePreferredDark().value);
  const toggleThemeMode = () => (dark.value = !dark.value);

  function generateAccentColorVariants(
    baseColor: string = state.text?.accentColor || '#7A7A7A',
    darkMode: boolean = dark.value
  ) {
    const lightenBy = darkMode ? 0.375 : 0.0;
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

  // all texts accent color variants
  const _allAccentColors = computed(() =>
    Object.fromEntries(
      pfData.value?.texts.map((t) => [
        t.id,
        generateAccentColorVariants(t.accentColor || '#7A7A7A', dark.value),
      ]) || []
    )
  );

  function getAccentColors(textId?: string | null) {
    return (
      _allAccentColors.value[textId || ''] || generateAccentColorVariants('#7A7A7A', dark.value)
    );
  }

  const custom = computed(() => ({
    mainBgColor: dark.value ? '#ffffff10' : '#00000010',
    contentBgColor: dark.value ? '#00000044' : '#ffffffcc',
    accent: getAccentColors(state.text?.id),
  }));

  const nuiBaseTheme = computed(() => (dark.value ? darkTheme : lightTheme));

  const nuiThemeOverrides = computed(() => {
    const primary = toRgba(custom.value.accent.base);
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
    const vars = {
      '--base-color': nuiBaseTheme.value.common.baseColor,
      '--text-color': nuiBaseTheme.value.common.textColor1,

      '--accent-color': custom.value.accent.base,
      '--accent-color-fade1': custom.value.accent.fade1,
      '--accent-color-fade2': custom.value.accent.fade2,
      '--accent-color-fade3': custom.value.accent.fade3,
      '--accent-color-fade4': custom.value.accent.fade4,
      '--accent-color-fade5': custom.value.accent.fade5,
      '--accent-color-spotlight': custom.value.accent.spotlight,

      '--link-color': custom.value.accent.base,
      '--link-color-hover': custom.value.accent.fade1,

      '--main-bg-color': custom.value.mainBgColor,
      '--content-bg-color': custom.value.contentBgColor,
    };
    Object.entries(vars).forEach(([k, v]) => {
      document.documentElement.style.setProperty(k, v);
    });
  });

  return {
    dark,
    toggleThemeMode,
    nuiBaseTheme,
    nuiThemeOverrides,
    custom,
    getAccentColors,
  };
});
