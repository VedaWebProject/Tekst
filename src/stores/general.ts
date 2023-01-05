import { ref } from 'vue';
import { defineStore } from 'pinia';

export const useGeneralAppState = defineStore('general', () => {
  const globalLoading = ref(false);
  const startGlobalLoading = () => {
    globalLoading.value = true;
  };
  const finishGlobalLoading = () =>
    setTimeout(() => {
      globalLoading.value = false;
    }, 100);

  return { globalLoading, startGlobalLoading, finishGlobalLoading };
});
