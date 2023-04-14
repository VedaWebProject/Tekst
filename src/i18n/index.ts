import staticI18nMsgs from '@intlify/unplugin-vue-i18n/messages';
import { createI18n } from 'vue-i18n';
import type { I18nOptions } from 'vue-i18n';
import type { NDateLocale } from 'naive-ui';
import { enUS, dateEnUS } from 'naive-ui';
import { deDE, dateDeDE } from 'naive-ui';
import { PlatformApi } from '@/openapi';
import { configureApi } from '@/openApiConfig';

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
  nUiLangLocale: any;
  nUiDateLocale: NDateLocale;
}

export const localeProfiles: { [localeKey: string]: AvailableLocale } = {
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

export const i18n = createI18n(i18nOptions);
const platformApi = configureApi(PlatformApi);

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
    // server data has to be loaded
    await platformApi.getTranslations({ lang: l }).then((response) => {
      i18n.global.mergeLocaleMessage(l, { server: response.data });
    });
  }

  // @ts-ignore
  i18n.global.locale.value = l;
  document.querySelector('html')?.setAttribute('lang', l);
  return Promise.resolve(localeProfiles[l]);
}
