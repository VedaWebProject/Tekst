import { createI18n } from 'vue-i18n';

import staticI18nMsgs from '@intlify/unplugin-vue-i18n/messages';

import type { I18n, I18nOptions } from 'vue-i18n';

const I18N_OPTIONS: I18nOptions = {
  legacy: false,
  globalInjection: true,
  locale: 'en',
  fallbackLocale: 'en',
  messages: staticI18nMsgs,
};

export function setupI18n(options: I18nOptions = I18N_OPTIONS) {
  const i18n = createI18n(options);
  setI18nLanguage(i18n, options.locale);
  return i18n;
}

export function setI18nLanguage(i18n: I18n, locale: I18nOptions['locale']) {
  if (i18n.mode === 'legacy') {
    // @ts-ignore
    i18n.global.locale = locale;
  } else {
    // @ts-ignore
    i18n.global.locale.value = locale;
  }
  /**
   * NOTE:
   * If you need to specify the language setting for headers, such as the `fetch` API, set it here.
   * The following is an example for axios.
   *
   * axios.defaults.headers.common['Accept-Language'] = locale
   */

  // set html lang attr
  locale && document.querySelector('html')?.setAttribute('lang', locale);
}
