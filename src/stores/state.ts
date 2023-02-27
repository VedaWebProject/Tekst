import { ref, computed } from 'vue';
import { defineStore } from 'pinia';
import type { TextRead } from '@/openapi';
import Color from 'color';
import { useSettingsStore } from './settings';

export const useStateStore = defineStore('state', () => {
  // global loading state
  const globalLoading = ref(false);
  const startGlobalLoading = () => {
    globalLoading.value = true;
  };
  const finishGlobalLoading = (delayMs: number = 0) =>
    setTimeout(() => {
      globalLoading.value = false;
    }, delayMs);

  // current text
  const text = ref<TextRead | null>(null);
  // current text accent color variants
  const settings = useSettingsStore();
  const accentColor = computed(() => {
    const lighten = settings.theme === 'dark' ? 0.2 : 0.0;
    const base = Color(text.value ? text.value.accentColor : '#41658a').lighten(lighten);
    return {
      base: base.hex(),
      intense: base.saturate(0.75).hex(),
      fade1: base.fade(0.2).hexa(),
      fade2: base.fade(0.4).hexa(),
      fade3: base.fade(0.6).hexa(),
      fade4: base.fade(0.8).hexa(),
      fade5: base.fade(0.9).hexa(),
    };
  });

  return {
    globalLoading,
    startGlobalLoading,
    finishGlobalLoading,
    text,
    accentColor,
  };
});
