import { ref, computed, watch } from 'vue';
import { defineStore } from 'pinia';
import { useWindowSize } from '@vueuse/core';
import type { RouteLocationNormalized } from 'vue-router';
import { i18n, setI18nLocale, localeProfiles, getAvaliableBrowserLocaleKey } from '@/i18n';
import type { AvailableLocale } from '@/i18n';
import { useRoute } from 'vue-router';
import type { TextRead } from '@/openapi';
import type { ThemeMode } from '@/theme';
import { useI18n } from 'vue-i18n';
import { usePlatformData } from '@/platformData';
import { useAuthStore } from './auth';

export const useStateStore = defineStore('state', () => {
  // define resources
  const { pfData } = usePlatformData();
  const route = useRoute();
  const auth = useAuthStore();
  const windowSize = useWindowSize();
  const { t, te } = useI18n({ useScope: 'global' });

  // theme
  const themeMode = ref<ThemeMode>((localStorage.getItem('theme') as ThemeMode) || 'light');
  watch(themeMode, (after) => localStorage.setItem('theme', after));

  function toggleThemeMode() {
    themeMode.value = themeMode.value === 'light' ? 'dark' : 'light';
  }

  // locale
  const locale = ref(
    auth.user?.locale ||
      localStorage.getItem('locale') ||
      getAvaliableBrowserLocaleKey() ||
      i18n.global.locale
  );
  const locales = i18n.global.availableLocales;
  watch(locale, (after) => {
    localStorage.setItem('locale', after);
    setPageTitle();
  });
  async function setLocale(
    l: string = locale.value,
    updateUserLocale: boolean = true
  ): Promise<AvailableLocale> {
    const lang = await setI18nLocale(l);
    locale.value = lang.key;
    if (updateUserLocale) {
      try {
        await auth.updateUser({ locale: localeProfiles[lang.key].apiLocaleEnum });
      } catch {
        // do sweet FA
      }
    }
    return lang;
  }

  // current text
  const text = ref<TextRead>();
  watch(route, (after) => {
    if ('text' in after.params && after.params.text && text.value?.slug !== after.params.text) {
      // use text from route OR default text
      text.value =
        pfData.value?.texts.find((t) => t.slug === after.params.text) ||
        pfData.value?.texts.find((t) => t.id === pfData.value?.settings.defaultTextId);
    }
  });
  watch(text, () => {
    setPageTitle(route);
    text.value && localStorage.setItem('text', text.value?.slug);
  });

  // fallback text for invalid text references
  const fallbackText = computed(
    () =>
      text.value ||
      pfData.value?.texts.find((t) => t.slug == localStorage.getItem('text')) ||
      pfData.value?.texts.find((t) => t.id === pfData.value?.settings.defaultTextId) ||
      pfData.value?.texts[0]
  );

  // global loading state
  const globalLoading = ref(false);
  const globalLoadingMsg = ref('');
  const globalLoadingProgress = ref(0);
  const startGlobalLoading = () => {
    globalLoading.value = true;
  };
  const finishGlobalLoading = async (delayMs: number = 0, resetLoadingDataDelayMs: number = 0) => {
    await new Promise((resolve) => setTimeout(resolve, delayMs));
    globalLoading.value = false;
    await new Promise((resolve) => setTimeout(resolve, resetLoadingDataDelayMs));
    globalLoadingMsg.value = '...';
    globalLoadingProgress.value = 0;
  };

  // small screen (< 860px)
  const smallScreen = computed(() => windowSize.width.value < 860);
  const dropdownSize = computed(() => (smallScreen.value ? 'huge' : undefined));

  // set page title
  function setPageTitle(forRoute?: RouteLocationNormalized) {
    const r = forRoute || route;
    const rTitle = te(`routes.pageTitle.${String(r.name)}`)
      ? t(`routes.pageTitle.${String(r.name)}`)
      : '';
    const tTitle = 'text' in r.params && text.value?.title && ` "${text.value?.title}"`;
    const pfName = pfData.value?.info?.platformName ? ` | ${pfData.value?.info?.platformName}` : '';
    document.title = `${rTitle || ''}${tTitle || ''}${pfName}`;
  }

  return {
    globalLoading,
    startGlobalLoading,
    finishGlobalLoading,
    globalLoadingMsg,
    globalLoadingProgress,
    smallScreen,
    dropdownSize,
    setPageTitle,
    themeMode,
    toggleThemeMode,
    locale,
    locales,
    text,
    fallbackText,
    setLocale,
  };
});
