import { STATIC_PATH } from '@/common';
import { useFetch, usePreferredDark } from '@vueuse/core';
import logo from '@/assets/logo.png';
import logoDarkmode from '@/assets/logo-darkmode.png';
import { computed, ref } from 'vue';
import { useThemeStore } from '@/stores';

const customLogo = `${STATIC_PATH}/logo.png`;
const customLogoDarkmode = `${STATIC_PATH}/logo-darkmode.png`;
const customLogoAvailable = ref(false);
const customLogoDarkmodeAvailable = ref(false);

(async () => {
  customLogoAvailable.value = await useFetch(customLogo).error.value;
  customLogoDarkmodeAvailable.value = await useFetch(customLogoDarkmode).error.value;
})();

export function useLogo() {
  const theme = useThemeStore();
  const darkPreferred = usePreferredDark();
  const logoLight = computed(() => (!customLogoAvailable.value ? logo : customLogo));
  const logoDark = computed(() => (!customLogoAvailable.value ? logoDarkmode : customLogoDarkmode));
  const pageLogo = computed(() => (theme.darkMode ? logoDark.value : logoLight.value));
  const favicon = computed(() => (darkPreferred.value ? logoDark.value : logoLight.value));
  return { pageLogo, favicon };
}
