import { ref, computed, watch } from 'vue';
import { defineStore } from 'pinia';
import { useWindowSize } from '@vueuse/core';
import type { RouteLocationNormalized } from 'vue-router';
import { i18n, setI18nLocale, localeProfiles, getAvaliableBrowserLocaleKey } from '@/i18n';
import type { AvailableLocale } from '@/i18n';
import { useRoute } from 'vue-router';
import type { TextRead } from '@/api';
import type { ThemeMode } from '@/theme';
import { $t, $te } from '@/i18n';
import { usePlatformData } from '@/platformData';
import { useAuthStore } from './auth';
import { useMessages } from '@/messages';

export const useStateStore = defineStore('state', () => {
  // define resources
  const { pfData } = usePlatformData();
  const route = useRoute();
  const auth = useAuthStore();
  const windowSize = useWindowSize();
  const { message } = useMessages();

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
    const lang = setI18nLocale(l);
    locale.value = lang.key;
    if (updateUserLocale && auth.user?.locale !== lang.key) {
      try {
        await auth.updateUser({ locale: localeProfiles[lang.key].key });
        message.info($t('account.localeUpdated', { locale: lang.displayFull }));
      } catch {
        // do sweet FA
      }
    }
    return lang;
  }

  // current text

  const text = ref<TextRead>();
  watch(
    () => route.params.text,
    (after) => {
      if (after && text.value?.slug !== after) {
        // use text from route OR default text
        text.value =
          pfData.value?.texts.find((t) => t.slug === after) ||
          pfData.value?.texts.find((t) => t.id === pfData.value?.settings.defaultTextId);
      }
    }
  );

  watch(
    () => text.value?.id,
    () => {
      setPageTitle(route);
      text.value && localStorage.setItem('text', text.value?.slug);
    }
  );

  // fallback text for invalid text references

  const fallbackText = computed(
    () =>
      text.value ||
      pfData.value?.texts.find((t) => t.slug == localStorage.getItem('text')) ||
      pfData.value?.texts.find((t) => t.id === pfData.value?.settings.defaultTextId) ||
      pfData.value?.texts[0]
  );

  // text level labels

  const textLevelLabels = computed(
    () =>
      text.value?.levels.map(
        (l) =>
          l.find((l) => l.locale === locale.value)?.label ||
          l.find((l) => l.locale === 'enUS')?.label ||
          (l.length > 0 && l[0].label) ||
          ''
      ) || []
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

  // responsiveness

  const smallScreen = computed(() => windowSize.width.value < 900);
  const dropdownSize = computed(() => (smallScreen.value ? 'huge' : undefined));

  // detect touch device
  const isTouchDevice = ref(true);
  window.addEventListener(
    'mouseover',
    function onFirstHover() {
      isTouchDevice.value = false;
    },
    { once: true }
  );

  // set page title
  function setPageTitle(forRoute: RouteLocationNormalized = route) {
    const title = $te(`routes.pageTitle.${String(forRoute.name)}`)
      ? $t(`routes.pageTitle.${String(forRoute.name)}`, {
          text: text.value?.title,
          username: auth.user?.username,
        })
      : undefined;
    const pfName = pfData.value?.settings.infoPlatformName;
    document.title = [title, pfName].filter(Boolean).join(' | ');
  }

  return {
    globalLoading,
    startGlobalLoading,
    finishGlobalLoading,
    globalLoadingMsg,
    globalLoadingProgress,
    smallScreen,
    dropdownSize,
    isTouchDevice,
    setPageTitle,
    themeMode,
    toggleThemeMode,
    locale,
    locales,
    text,
    fallbackText,
    textLevelLabels,
    setLocale,
  };
});
