import type { LocaleKey, TextRead, TranslationLocaleKey } from '@/api';
import { usePlatformData } from '@/composables/platformData';
import type { LocaleProfile } from '@/i18n';
import { $t, $te, getAvaliableBrowserLocaleKey, localeProfiles, setI18nLocale } from '@/i18n';
import { useAuthStore } from '@/stores/auth';
import { pickTranslation } from '@/utils';
import { StorageSerializers, useStorage, useWindowSize } from '@vueuse/core';
import { defineStore } from 'pinia';
import { computed, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import type { RouteLocationNormalized } from 'vue-router';
import { useRoute } from 'vue-router';

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
  const { width: windowWidth } = useWindowSize({ type: 'visual' });
  const { locale: i18nLocale } = useI18n({ useScope: 'global' });

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

  const locale = useStorage<LocaleKey>(
    'locale',
    auth.user?.locale || getAvaliableBrowserLocaleKey() || (i18nLocale.value as LocaleKey) || 'enUS'
  );
  watch(locale, () => {
    setPageTitle();
  });

  const availableLocales = computed(() =>
    localeProfiles.filter((lp) => !!pfData.value?.state.availableLocales.includes(lp.key))
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
    const availableLocaleKeys = pfData.value?.state.availableLocales as LocaleKey[] | undefined;
    const effectiveLocale = await setI18nLocale(
      availableLocaleKeys?.find((al) => al === l) || 'enUS'
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
  const textSlug = useStorage<TextRead['slug']>('text', null, undefined, {
    serializer: StorageSerializers.string,
  });
  watch(
    () => route.params.textSlug,
    (after) => {
      if (after && text.value?.slug !== after) {
        // use text from route OR default text
        text.value =
          pfData.value?.texts.find((t) => t.slug === after) ||
          pfData.value?.texts.find((t) => t.id === pfData.value?.state.defaultTextId);
      }
    }
  );

  watch(
    () => text.value?.id,
    () => {
      setPageTitle(route);
      if (text.value) textSlug.value = text.value.slug;
    }
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

  const smallScreen = computed(() => windowWidth.value < 900);

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
    const pfName = pfData.value?.state.platformName;
    document.title = [title, pfName].filter(Boolean).join(' | ');
  }

  return {
    init,
    smallScreen,
    isTouchDevice,
    backtopVisible,
    setPageTitle,
    locale,
    setLocale,
    availableLocales,
    translationLocaleOptions,
    text,
    textSlug,
    textsProps,
    textLevelLabels,
    getTextLevelLabel,
  };
});
