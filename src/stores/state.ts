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
  // current text accent color variants
  const accentColor = computed(() => {
    const base = text.value ? text.value.accentColor : '#0f0';
    return {
      opaque: base,
      translucent20: Color(base).fade(0.2).hexa(),
      translucent40: Color(base).fade(0.4).hexa(),
      translucent60: Color(base).fade(0.6).hexa(),
      translucent80: Color(base).fade(0.8).hexa(),
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
