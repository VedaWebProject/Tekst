import staticI18nMsgs from '@intlify/unplugin-vue-i18n/messages';

import { createI18n } from 'vue-i18n';
import type { I18nOptions } from 'vue-i18n';

import type { NDateLocale } from 'naive-ui';

import { enUS, dateEnUS } from 'naive-ui';
import { deDE, dateDeDE } from 'naive-ui';
import { UidataApi } from 'textrig-ts-client';

const I18N_OPTIONS: I18nOptions = {
  legacy: false,
  globalInjection: true,
  locale: 'enUS',
  fallbackLocale: 'enUS',
  messages: staticI18nMsgs,
};

export interface AvailableLanguage {
  key: string;
  displayFull: string;
  displayShort: string;
  icon: string;
  nUiLangLocale: any;
  nUiDateLocale: NDateLocale;
}

export const LANGUAGES: { [localeKey: string]: AvailableLanguage } = {
  enUS: {
    key: 'enUS',
    displayFull: 'English (US)',
    displayShort: 'en-US',
    icon: '🇺🇸',
    nUiLangLocale: enUS,
    nUiDateLocale: dateEnUS,
  },
  deDE: {
    key: 'deDE',
    displayFull: 'Deutsch',
    displayShort: 'de-DE',
    icon: '🇩🇪',
    nUiLangLocale: deDE,
    nUiDateLocale: dateDeDE,
  },
};

export const i18n = createI18n(I18N_OPTIONS);
const uiDataApi = new UidataApi();

export async function setI18nLanguage(
  locale: I18nOptions['locale'] = i18n.global.locale
): Promise<AvailableLanguage> {
  // @ts-ignore
  const l = locale?.value ?? locale ?? i18n.global.locale.value;
  if (!l) return Promise.reject(`Invalid locale code: ${l}`);

  try {
    await uiDataApi.uidataI18n({ lang: l }).then((data) => {
      i18n.global.mergeLocaleMessage(l, data);
    });
  } finally {
    // @ts-ignore
    i18n.global.locale.value = l;
    document.querySelector('html')?.setAttribute('lang', l);
  }

  return LANGUAGES[l];
}
