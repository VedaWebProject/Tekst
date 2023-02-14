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

  // login and registration modal state
  const showLogin = ref(false);
  const showRegistration = ref(false);
  const openLogin = () => {
    showRegistration.value = false;
    showLogin.value = true;
  };
  const openRegistration = () => {
    showLogin.value = false;
    showRegistration.value = true;
  };

  return {
    globalLoading,
    startGlobalLoading,
    finishGlobalLoading,
    showLogin,
    showRegistration,
    openLogin,
    openRegistration,
  };
});
