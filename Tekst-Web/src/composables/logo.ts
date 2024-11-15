import faviconIcoDarkmode from '@/assets/favicon-darkmode.ico';
import faviconPngDarkmode from '@/assets/favicon-darkmode.png';
import faviconIco from '@/assets/favicon.ico';
import faviconPng from '@/assets/favicon.png';
import logoDarkmode from '@/assets/logo-darkmode.png';
import logo from '@/assets/logo.png';
import { STATIC_PATH } from '@/common';
import { useThemeStore } from '@/stores';
import { useFetch, usePreferredDark } from '@vueuse/core';
import { computed, ref, type Ref } from 'vue';

interface LogoImage {
  url?: string;
  custom: string;
  fallback: string;
}

// define possible custom images
const imgs: Ref<{ [key: string]: LogoImage }> = ref({
  logoPng: { custom: `${STATIC_PATH}/logo.png`, fallback: logo },
  logoPngDark: { custom: `${STATIC_PATH}/logo-darkmode.png`, fallback: logoDarkmode },
  favPng: { custom: `${STATIC_PATH}/favicon.png`, fallback: faviconPng },
  favPngDark: { custom: `${STATIC_PATH}/favicon-darkmode.png`, fallback: faviconPngDarkmode },
  favIco: { custom: `${STATIC_PATH}/favicon.ico`, fallback: faviconIco },
  favIcoDark: { custom: `${STATIC_PATH}/favicon-darkmode.ico`, fallback: faviconIcoDarkmode },
});

// check whether custom images exist and set URLs accordingly
Object.values(imgs.value).forEach(async (img) => {
  img.url =
    (await useFetch(img.custom).head()).statusCode.value === 200 ? img.custom : img.fallback;
});

export function useLogo() {
  const theme = useThemeStore();
  const darkPref = usePreferredDark();
  const pageLogo = computed(() =>
    theme.darkMode ? imgs.value.logoPngDark.url || imgs.value.logoPng.url : imgs.value.logoPng.url
  );
  const faviconPng = computed(() =>
    darkPref.value
      ? imgs.value.favPngDark.url ||
        imgs.value.logoPngDark.url ||
        imgs.value.favPng.url ||
        imgs.value.logoPng.url
      : imgs.value.favPng.url || imgs.value.logoPng.url
  );
  const faviconIco = computed(() =>
    darkPref.value ? imgs.value.favIcoDark.url || imgs.value.favIco.url : imgs.value.favIco.url
  );
  return { pageLogo, faviconPng, faviconIco };
}
