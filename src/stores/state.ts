import { ref, computed } from 'vue';
import { defineStore } from 'pinia';
import type { TextRead } from '@/openapi';
import Color from 'color';

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
  const accentColor = computed(() => {
    const base = text.value ? text.value.accentColor : '#0f0';
    return {
      plain: base,
      light: Color(base).lighten(0.6).hex(),
      lighter: Color(base).lighten(0.8).hex(),
      dark: Color(base).darken(0.4).hex(),
      darker: Color(base).darken(0.6).hex(),
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
