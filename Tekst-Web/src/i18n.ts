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
export const $t: typeof i18n.global.t = i18n.global.t;
export const $te: typeof i18n.global.te = i18n.global.te;

// @ts-expect-error typing for i18n.global.locale is wrong when not in legacy mode;
// see https://vue-i18n.intlify.dev/guide/essentials/scope.html#local-scope-1
i18n.global.locale.value = 'enUS';

export function getLocaleProfile(localeKey: string): LocaleProfile | undefined {
  return localeProfiles.find((lp) => lp.key === localeKey);
}

export function setI18nLocale(
  // @ts-expect-error same as above :(
  newLocale: I18nOptions['locale'] = i18n.global.locale.value
): LocaleProfile {
  const l = unref(newLocale);
  // @ts-expect-error same as above :(
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
