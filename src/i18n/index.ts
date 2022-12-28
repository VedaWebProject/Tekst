import { createI18n } from 'vue-i18n';
import axios from 'axios';

import staticI18nMsgs from '@intlify/unplugin-vue-i18n/messages';

import type { I18nOptions } from 'vue-i18n';

const I18N_OPTIONS: I18nOptions = {
  legacy: false,
  globalInjection: true,
  locale: 'en',
  fallbackLocale: 'en',
  messages: staticI18nMsgs,
};

export const i18n = createI18n(I18N_OPTIONS);

export async function setI18nLanguage(locale: I18nOptions['locale']) {
  // @ts-ignore
  const l = locale?.value ?? i18n.global.locale.value;

  // fetch server i18n data
  const serverI18nMsgs = await axios
    .get(`${import.meta.env.TEXTRIG_SERVER_API}/uidata/i18n?lang=${l}`)
    .then((response) => response.data)
    .catch((error) => {
      console.error(error);
      console.error('Error loading translated (i18n) server resources');
    });

  i18n.global.mergeLocaleMessage(l, serverI18nMsgs);

  // @ts-ignore
  i18n.global.locale.value = l;

  // set default 'Accept-Language' header for axios
  axios.defaults.headers.common['Accept-Language'] = l;

  // set html lang attr
  document.querySelector('html')?.setAttribute('lang', l);
}
