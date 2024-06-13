import { STATIC_PATH } from '@/common';
import { useFetch, usePreferredDark } from '@vueuse/core';
import logo from '@/assets/logo.png';
import logoDarkmode from '@/assets/logo-darkmode.png';
import { computed } from 'vue';
import { useThemeStore } from '@/stores';

const customLogo = `${STATIC_PATH}/logo.png`;
const customLogoDarkmode = `${STATIC_PATH}/logo-darkmode.png`;
const { isFetching: fetchingCustomLogo, error: customLogoError } = await useFetch(customLogo);
const { isFetching: fetchingCustomDarkLogo, error: customDarkLogoError } =
  await useFetch(customLogoDarkmode);

export function useLogo() {
  const theme = useThemeStore();
  const darkPreferred = usePreferredDark();
  const logoLight = computed(() =>
    customLogoError.value || fetchingCustomLogo.value ? logo : customLogo
  );
  const logoDark = computed(() =>
    customDarkLogoError.value || fetchingCustomDarkLogo.value ? logoDarkmode : customLogoDarkmode
  );
  const pageLogo = computed(() => (theme.darkMode ? logoDark.value : logoLight.value));
  const favicon = computed(() => (darkPreferred.value ? logoDark.value : logoLight.value));
  return { pageLogo, favicon };
}
