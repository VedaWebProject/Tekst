import { ref, computed } from 'vue';
import { defineStore } from 'pinia';
import { useWindowSize } from '@vueuse/core';
import type { TextRead } from '@/openapi';
import Color from 'color';
import { useSettingsStore } from './settings';

export const useStateStore = defineStore('state', () => {
  // global loading state
  const globalLoading = ref(false);
  const globalLoadingMsg = ref('');
  const globalLoadingProgress = ref(0);
  const startGlobalLoading = () => {
    globalLoading.value = true;
  };
  const finishGlobalLoading = async (delayMs: number = 0, resetLoadingDataDelayMs: number = 0) => {
    await new Promise((resolve) => setTimeout(resolve, delayMs));
    globalLoading.value = false;
    await new Promise((resolve) => setTimeout(resolve, resetLoadingDataDelayMs));
    globalLoadingMsg.value = '...';
    globalLoadingProgress.value = 0;
  };

  // small screen (< 860px)
  const { width } = useWindowSize();
  const smallScreen = computed(() => width.value < 860);

  // current text
  const text = ref<TextRead | null>(null);

  // current text accent color variants
  const settings = useSettingsStore();
  const accentColor = computed(() => {
    const lighten = settings.theme === 'dark' ? 0.2 : 0.0;
    const base = Color(text.value ? text.value.accentColor : '#18A058').lighten(lighten);
    return {
      base: base.hex(),
      intense: base.saturate(0.5).hex(),
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
    globalLoadingMsg,
    globalLoadingProgress,
    smallScreen,
    text,
    accentColor,
  };
});
