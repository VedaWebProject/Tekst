import { STATIC_PATH } from '@/common';
import { useFetch, usePreferredDark } from '@vueuse/core';
import logo from '@/assets/logo.png';
import logoDarkmode from '@/assets/logo-darkmode.png';
import { computed, ref } from 'vue';
import { useThemeStore } from '@/stores';

const customLogo = `${STATIC_PATH}/logo.png`;
const customLogoDark = `${STATIC_PATH}/logo-darkmode.png`;
const logoLight = ref<string>();
const logoDark = ref<string>();

(async () => {
  logoLight.value = !(await useFetch(customLogo)).error.value ? customLogo : logo;
  logoDark.value = !(await useFetch(customLogoDark)).error.value ? customLogoDark : logoDarkmode;
})();

export function useLogo() {
  const theme = useThemeStore();
  const darkPreferred = usePreferredDark();
  const pageLogo = computed(() => (theme.darkMode ? logoDark.value : logoLight.value));
  const favicon = computed(() => (darkPreferred.value ? logoDark.value : logoLight.value));
  return { pageLogo, favicon };
}
