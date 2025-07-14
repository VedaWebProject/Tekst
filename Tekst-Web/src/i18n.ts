import type { LocaleKey } from '@/api';
import type { NDateLocale, NLocale, SelectOption } from 'naive-ui';
import { dateDeDE, dateEnUS, deDE, enUS } from 'naive-ui';
import { unref } from 'vue';
import type { I18nOptions } from 'vue-i18n';
import { createI18n } from 'vue-i18n';

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
    key: 'enUS',
    displayFull: 'English (US)',
    displayShort: 'en-US',
    icon: '🇺🇸',
    nUiLangLocale: enUS,
    nUiDateLocale: dateEnUS,
  },
  {
    key: 'deDE',
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
};

export const i18n = createI18n(i18nOptions);
export const $t: typeof i18n.global.t = i18n.global.t;
export const $te: typeof i18n.global.te = i18n.global.te;

// @ts-expect-error typing for i18n.global.locale is wrong when not in legacy mode;
// see https://vue-i18n.intlify.dev/guide/essentials/scope.html#local-scope-1
i18n.global.locale.value = 'enUS';
await setI18nLocale(); // load and set initial (default) locale

export function getLocaleProfile(localeKey: string): LocaleProfile | undefined {
  return localeProfiles.find((lp) => lp.key === localeKey);
}

export async function setI18nLocale(
  // @ts-expect-error same as above :(
  newLocale: LocaleKey = i18n.global.locale.value
): Promise<LocaleProfile> {
  const l = unref(newLocale);
  // load translations for this locale
  i18n.global.setLocaleMessage(l, (await import(`@/assets/i18n/ui/${l}.json`)).default);
  // set the new locale
  // @ts-expect-error same as above :(
  i18n.global.locale.value = l;
  // set the HTML lang attribute
  document.querySelector('html')?.setAttribute('lang', l);
  // return the locale profile, fall back to English if not found
  return getLocaleProfile(l) || (await setI18nLocale('enUS'));
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
