import { createI18n } from 'vue-i18n';

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

export async function setI18nLanguage(locale: I18nOptions['locale'] = i18n.global.locale) {
  // @ts-ignore
  const l = locale?.value ?? locale ?? i18n.global.locale.value;
  if (!l) return Promise.reject(`Invalid locale code: ${l}`);
  // @ts-ignore
  i18n.global.locale.value = l;
  document.querySelector('html')?.setAttribute('lang', l);
  // fetch server i18n data
  return await fetch(`${import.meta.env.TEXTRIG_SERVER_API}/uidata/i18n?lang=${l}`)
    .then((response) => {
      if (!response.ok) throw new Error('foo');
      return response;
    })
    .then((response) => response.json())
    .then((data) => {
      i18n.global.mergeLocaleMessage(l, data);
    });
}
