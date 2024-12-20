import { usePlatformData } from '@/composables/platformData';
import { useStateStore } from '@/stores';
import { darkOverrides, lightOverrides } from '@/themeOverrides';
import { usePreferredDark, useStorage } from '@vueuse/core';
import { adjustHue, lighten, saturate, toRgba, transparentize } from 'color2k';
import { darkTheme, lightTheme } from 'naive-ui';
import { defineStore } from 'pinia';
import { computed } from 'vue';

export declare type ThemeMode = 'light' | 'dark';

export const useThemeStore = defineStore('theme', () => {
  const state = useStateStore();
  const { pfData } = usePlatformData();
  const browserDarkThemePreferred = usePreferredDark();
  const darkMode = useStorage<boolean>('darkMode', browserDarkThemePreferred.value || false);
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
