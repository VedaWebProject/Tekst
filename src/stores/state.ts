import { ref } from 'vue';
import { defineStore } from 'pinia';

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

  return {
    globalLoading,
    startGlobalLoading,
    finishGlobalLoading,
  };
});
