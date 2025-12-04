import tekstFaviconIcoDark from '@/assets/favicon-dark.ico';
import tekstFaviconPngDark from '@/assets/favicon-dark.png';
import tekstFaviconIco from '@/assets/favicon.ico';
import tekstFaviconPng from '@/assets/favicon.png';
import tekstLogoDark from '@/assets/logo-dark.png';
import tekstLogo from '@/assets/logo.png';
import env from '@/env';
import { useThemeStore } from '@/stores';
import { useFetch, usePreferredDark } from '@vueuse/core';
import { computed } from 'vue';

const _resolve = async (url: string): Promise<string | null> =>
  (await useFetch(url).head()).statusCode.value === 200 ? url : null;

// define possible custom images
const custom: Record<string, string | null> = {
  logoPng: await _resolve(`${env.STATIC_PATH}/logo.png`),
  logoPngDark: await _resolve(`${env.STATIC_PATH}/logo-dark.png`),
  favPng: await _resolve(`${env.STATIC_PATH}/favicon.png`),
  favPngDark: await _resolve(`${env.STATIC_PATH}/favicon-dark.png`),
  favIco: await _resolve(`${env.STATIC_PATH}/favicon.ico`),
  favIcoDark: await _resolve(`${env.STATIC_PATH}/favicon-dark.ico`),
};

export function useLogo() {
  const theme = useThemeStore();
  const darkPref = usePreferredDark();
  const pageLogo = computed(() =>
    theme.dark
      ? custom.logoPngDark ?? custom.logoPng ?? tekstLogoDark
      : custom.logoPng ?? tekstLogo
  );
  const faviconPng = computed(() =>
    darkPref.value
      ? custom.favPngDark ?? custom.favPng ?? tekstFaviconPngDark
      : custom.favPng ?? custom.favPngDark ?? tekstFaviconPng
  );
  const faviconIco = computed(() =>
    darkPref.value
      ? custom.favIcoDark ?? custom.favIco ?? tekstFaviconIcoDark
      : custom.favIco ?? custom.favIcoDark ?? tekstFaviconIco
  );
  return { pageLogo, faviconPng, faviconIco };
}
