import { createI18n } from 'vue-i18n';
import axios from 'axios';

import staticI18nMsgs from '@intlify/unplugin-vue-i18n/messages';

import type { I18n, I18nOptions } from 'vue-i18n';

const I18N_OPTIONS: I18nOptions = {
  legacy: false,
  globalInjection: true,
  locale: 'en',
  fallbackLocale: 'en',
};

async function setupI18n(options: I18nOptions = I18N_OPTIONS) {
  // fetch server i18n data
  const serverI18nMsgs = await axios
    .get(import.meta.env.TEXTRIG_SERVER_API + '/uidata/i18n')
    .then((response) => response.data)
    .catch((error) => {
      console.error(error);
      console.error('Error loading translated (i18n) server resources');
    });
  // merge static and server i18n messages
  options.messages = {
    ...staticI18nMsgs,
    ...serverI18nMsgs,
  };
  const i18n = createI18n(options);
  setI18nLanguage(options.locale, i18n);
  return i18n;
}

export const i18n = await setupI18n();

export function setI18nLanguage(locale: I18nOptions['locale'], i18nInstance: I18n = i18n) {
  const l = locale ?? String(i18nInstance.global.locale);
  if (i18nInstance.mode === 'legacy') {
    // @ts-ignore
    i18nInstance.global.locale = l;
  } else {
    // @ts-ignore
    i18nInstance.global.locale.value = l;
  }

  // set default 'Accept-Language' header for axios
  axios.defaults.headers.common['Accept-Language'] = l;

  // set html lang attr
  document.querySelector('html')?.setAttribute('lang', l);
}
