import { ref, computed, watch } from 'vue';
import { defineStore } from 'pinia';
import { useWindowSize } from '@vueuse/core';
import type { RouteLocationNormalized } from 'vue-router';
import { i18n, setI18nLocale, getAvaliableBrowserLocaleKey, localeProfiles } from '@/i18n';
import type { LocaleProfile } from '@/i18n';
import { useRoute } from 'vue-router';
import type { TextRead, TranslationLocaleKey } from '@/api';
import { $t, $te } from '@/i18n';
import { usePlatformData } from '@/composables/platformData';
import { useAuthStore } from './auth';
import type { LocaleKey } from '@/api';
import { pickTranslation } from '@/utils';

interface AppInitState {
  progress: number;
  stepMsg: string;
  loading: boolean;
  initialized: boolean;
  authChecked: boolean;
  error: boolean;
}

export const useStateStore = defineStore('state', () => {
  // define resources
  const { pfData } = usePlatformData();
  const route = useRoute();
  const auth = useAuthStore();
  const windowSize = useWindowSize();

  // app init
  const init = ref<AppInitState>({
    progress: 0,
    stepMsg: '',
    loading: true,
    initialized: false,
    authChecked: false,
    error: false,
  });

  // locale

  const locale = ref<LocaleKey>(
    (auth.user?.locale ||
      localStorage.getItem('locale') ||
      getAvaliableBrowserLocaleKey() ||
      i18n.global.locale) as LocaleKey
  );
  watch(locale, (after) => {
    localStorage.setItem('locale', after);
    setPageTitle();
  });

  const availableLocales = computed(() =>
    localeProfiles.filter((lp) => !!pfData.value?.settings.availableLocales?.includes(lp.key))
  );

  const translationLocaleOptions = computed<
    {
      label: string;
      value: TranslationLocaleKey;
    }[]
  >(() =>
    [
      {
        label: `🌐 ${$t('models.locale.allLanguages')}`,
        value: '*' as TranslationLocaleKey,
      },
    ].concat(
      availableLocales.value.map((locale) => ({
        label: `${locale.icon} ${locale.displayFull}`,
        value: locale.key as TranslationLocaleKey,
      }))
    )
  );

  async function setLocale(
    l: string = locale.value,
    updateUserLocale: boolean = true
  ): Promise<LocaleProfile> {
    const availableLocaleKeys = pfData.value?.settings.availableLocales;
    const effectiveLocale = setI18nLocale(
      availableLocaleKeys?.find((al) => al === l) || availableLocaleKeys?.[0] || 'enUS'
    );
    locale.value = effectiveLocale.key;
    if (updateUserLocale && auth.loggedIn && auth.user?.locale !== effectiveLocale.key) {
      try {
        await auth.updateUser({ locale: effectiveLocale.key });
      } catch {
        // do sweet FA
      }
    }
    return effectiveLocale;
  }

  // text ID – text props mapping
  const textsProps = computed(() =>
    Object.fromEntries(
      pfData.value?.texts.map((t) => [
        t.id,
        {
          title: t.title,
          accentColor: t.accentColor,
        },
      ]) || []
    )
  );

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

  function getTextLevelLabel(textId: string, level: number, localeKey: LocaleKey = locale.value) {
    return (
      pickTranslation(pfData.value?.texts.find((t) => t.id === textId)?.levels[level], localeKey) ||
      ''
    );
  }

  const textLevelLabels = computed(
    () => text.value?.levels.map((l) => pickTranslation(l, locale.value)) || []
  );

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

  // tasks widget visibility
  const backtopVisible = ref(false);

  // set page title
  function setPageTitle(
    forRoute: RouteLocationNormalized = route,
    variables: Record<string, string> = {}
  ) {
    const title = $te(`routes.pageTitle.${String(forRoute.name)}`)
      ? $t(`routes.pageTitle.${String(forRoute.name)}`, {
          text: text.value?.title,
          ...variables,
        })
      : undefined;
    const pfName = pfData.value?.settings.platformName;
    document.title = [title, pfName].filter(Boolean).join(' | ');
  }

  return {
    init,
    smallScreen,
    dropdownSize,
    isTouchDevice,
    backtopVisible,
    setPageTitle,
    locale,
    setLocale,
    availableLocales,
    translationLocaleOptions,
    text,
    textsProps,
    fallbackText,
    textLevelLabels,
    getTextLevelLabel,
  };
});
