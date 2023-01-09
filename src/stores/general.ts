import { ref } from 'vue';
import { defineStore } from 'pinia';

export const useAppStateStore = defineStore('appState', () => {
  const globalLoading = ref(false);
  const startGlobalLoading = () => {
    globalLoading.value = true;
  };
  const finishGlobalLoading = (delayMs: number = 0) =>
    setTimeout(() => {
      globalLoading.value = false;
    }, delayMs);

  return {
    globalLoading,
    startGlobalLoading,
    finishGlobalLoading,
  };
});
