import staticI18nMsgs from '@intlify/unplugin-vue-i18n/messages';
import { createI18n } from 'vue-i18n';
import type { I18nOptions } from 'vue-i18n';
import type { NDateLocale, NLocale } from 'naive-ui';
import { enUS, dateEnUS } from 'naive-ui';
import { deDE, dateDeDE } from 'naive-ui';
import { useApi } from '@/api';
import { UserUpdateLocaleEnum } from '@/openapi';

const i18nOptions: I18nOptions = {
  legacy: false,
  globalInjection: true,
  locale: 'enUS',
  fallbackLocale: 'enUS',
  messages: staticI18nMsgs,
};

export interface AvailableLocale {
  key: string;
  displayFull: string;
  displayShort: string;
  icon: string;
  nUiLangLocale: NLocale;
  nUiDateLocale: NDateLocale;
  apiLocaleEnum: UserUpdateLocaleEnum;
}

export const localeProfiles: { [localeKey: string]: AvailableLocale } = {
  enUS: {
    key: 'enUS',
    displayFull: 'English (US)',
    displayShort: 'en-US',
    icon: '🇺🇸',
    nUiLangLocale: enUS,
    nUiDateLocale: dateEnUS,
    apiLocaleEnum: UserUpdateLocaleEnum.EnUs,
  },
  deDE: {
    key: 'deDE',
    displayFull: 'Deutsch',
    displayShort: 'de-DE',
    icon: '🇩🇪',
    nUiLangLocale: deDE,
    nUiDateLocale: dateDeDE,
    apiLocaleEnum: UserUpdateLocaleEnum.DeDe,
  },
};

export const i18n = createI18n(i18nOptions);
const { platformApi } = useApi();

// set initial i18n locale
// @ts-ignore
i18n.global.locale.value = localStorage.getItem('locale') || 'enUS';

async function loadServerTranslations(locale: string) {
  await platformApi.getTranslations({ lang: locale }).then((response) => {
    i18n.global.mergeLocaleMessage(locale, { server: response.data });
  });
}

export async function setI18nLocale(
  locale: I18nOptions['locale'] = i18n.global.locale
): Promise<AvailableLocale> {
  // @ts-ignore
  const l = locale ?? locale.value ?? i18n.global.locale.value;

  if (!l) {
    // passed locale is invalid
    return Promise.reject(`Invalid locale code: ${l}`);
  }

  if (!i18n.global.te('server', l)) {
    await loadServerTranslations(l);
  }

  // @ts-ignore
  i18n.global.locale.value = l;
  document.querySelector('html')?.setAttribute('lang', l);
  return Promise.resolve(localeProfiles[l]);
}

export function getAvaliableBrowserLocaleKey() {
  return window.navigator.languages
    .map((l) => localeProfiles[l.replace(/[^a-zA-Z]/, '')])
    .find((l) => !!l)?.key;
}
