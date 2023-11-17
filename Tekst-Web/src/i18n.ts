import staticI18nMsgs from '@intlify/unplugin-vue-i18n/messages';
import { createI18n } from 'vue-i18n';
import type { I18nOptions } from 'vue-i18n';
import type { NDateLocale, NLocale } from 'naive-ui';
import { enUS, dateEnUS } from 'naive-ui';
import { deDE, dateDeDE } from 'naive-ui';
import { unref } from 'vue';

export enum LocaleKey {
  EnUs = 'enUS',
  DeDe = 'deDE',
}

export interface AvailableLocale {
  key: LocaleKey;
  displayFull: string;
  displayShort: string;
  icon: string;
  nUiLangLocale: NLocale;
  nUiDateLocale: NDateLocale;
}

export const localeProfiles: { [localeKey: string]: AvailableLocale } = {
  enUS: {
    key: LocaleKey.EnUs,
    displayFull: 'English (US)',
    displayShort: 'en-US',
    icon: '🇺🇸',
    nUiLangLocale: enUS,
    nUiDateLocale: dateEnUS,
  },
  deDE: {
    key: LocaleKey.DeDe,
    displayFull: 'Deutsch',
    displayShort: 'de-DE',
    icon: '🇩🇪',
    nUiLangLocale: deDE,
    nUiDateLocale: dateDeDE,
  },
};

const i18nOptions: I18nOptions = {
  legacy: false,
  globalInjection: true,
  locale: 'enUS',
  fallbackLocale: 'enUS',
  messages: staticI18nMsgs,
};

export const i18n = createI18n(i18nOptions);
export const { t: $t, te: $te, tm: $tm, tc: $tc } = i18n.global;

// set initial i18n locale
// @ts-ignore
i18n.global.locale.value = localStorage.getItem('locale') || 'enUS';

export function setI18nLocale(locale: I18nOptions['locale'] = i18n.global.locale): AvailableLocale {
  const l = unref(locale) ?? i18n.global.locale;
  if (!l) {
    // passed locale is invalid
    console.error(`Invalid locale code: ${l}`);
    return localeProfiles['enUS'];
  }
  // @ts-ignore
  i18n.global.locale.value = l;
  document.querySelector('html')?.setAttribute('lang', l);
  return localeProfiles[l];
}

export function getAvaliableBrowserLocaleKey() {
  return window.navigator.languages
    .map((l) => localeProfiles[l.replace(/[^a-zA-Z]/, '')])
    .find((l) => !!l)?.key;
}
