import faviconIcoDarkmode from '@/assets/favicon-darkmode.ico';
import faviconPngDarkmode from '@/assets/favicon-darkmode.png';
import faviconIco from '@/assets/favicon.ico';
import faviconPng from '@/assets/favicon.png';
import logoDarkmode from '@/assets/logo-darkmode.png';
import logo from '@/assets/logo.png';
import { useThemeStore } from '@/stores';
import { useFetch, usePreferredDark } from '@vueuse/core';
import { computed, ref, type Ref } from 'vue';
import env from '@/env';

interface LogoImage {
  url?: string;
  custom: string;
  fallback: string;
}

// define possible custom images
const imgs: Ref<{ [key: string]: LogoImage }> = ref({
  logoPng: {
    custom: `${env.STATIC_PATH}/logo.png`,
    fallback: logo,
  },
  logoPngDark: {
    custom: `${env.STATIC_PATH}/logo-darkmode.png`,
    fallback: logoDarkmode,
  },
  favPng: {
    custom: `${env.STATIC_PATH}/favicon.png`,
    fallback: faviconPng,
  },
  favPngDark: {
    custom: `${env.STATIC_PATH}/favicon-darkmode.png`,
    fallback: faviconPngDarkmode,
  },
  favIco: {
    custom: `${env.STATIC_PATH}/favicon.ico`,
    fallback: faviconIco,
  },
  favIcoDark: {
    custom: `${env.STATIC_PATH}/favicon-darkmode.ico`,
    fallback: faviconIcoDarkmode,
  },
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
    theme.dark ? imgs.value.logoPngDark.url || imgs.value.logoPng.url : imgs.value.logoPng.url
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
