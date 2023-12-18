import staticI18nMsgs from '@intlify/unplugin-vue-i18n/messages';
import { createI18n } from 'vue-i18n';
import type { I18nOptions } from 'vue-i18n';
import type { NDateLocale, NLocale, SelectOption } from 'naive-ui';
import { enUS, dateEnUS } from 'naive-ui';
import { deDE, dateDeDE } from 'naive-ui';
import { unref } from 'vue';

export enum LocaleKey {
  EnUs = 'enUS',
  DeDe = 'deDE',
}

export interface LocaleProfile {
  key: LocaleKey;
  displayFull: string;
  displayShort: string;
  icon: string;
  nUiLangLocale: NLocale;
  nUiDateLocale: NDateLocale;
}

export const localeProfiles: LocaleProfile[] = [
  {
    key: LocaleKey.EnUs,
    displayFull: 'English (US)',
    displayShort: 'en-US',
    icon: '🇺🇸',
    nUiLangLocale: enUS,
    nUiDateLocale: dateEnUS,
  },
  {
    key: LocaleKey.DeDe,
    displayFull: 'Deutsch',
    displayShort: 'de-DE',
    icon: '🇩🇪',
    nUiLangLocale: deDE,
    nUiDateLocale: dateDeDE,
  },
];

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
//(happens before app init, where locale is set respecting platform settings)
// @ts-ignore
i18n.global.locale.value = 'enUS';

export function getLocaleProfile(localeKey: string): LocaleProfile | undefined {
  return localeProfiles.find((lp) => lp.key === localeKey);
}

export function setI18nLocale(locale: I18nOptions['locale'] = i18n.global.locale): LocaleProfile {
  const l = unref(locale) ?? i18n.global.locale;
  if (!l) {
    // passed locale is invalid
    console.error(`Invalid locale code: ${l}`);
    return getLocaleProfile('enUS') || localeProfiles[0];
  }
  // @ts-ignore
  i18n.global.locale.value = l;
  document.querySelector('html')?.setAttribute('lang', l);
  return getLocaleProfile(l) || localeProfiles[0];
}

export function getAvaliableBrowserLocaleKey() {
  return window.navigator.languages
    .map((l) => getLocaleProfile(l.replace(/[^a-zA-Z]/, '')))
    .find((l) => !!l)?.key;
}

export function renderLanguageOptionLabel(availableOptions: SelectOption[], option: SelectOption) {
  return availableOptions.find((lo) => lo.value === option.value)
    ? (option.label as string)
    : `⚠ ${$t('i18n.invalidLanguage')} (${option.value})`;
}
