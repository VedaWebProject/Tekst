import { createApp } from 'vue';
import { createPinia } from 'pinia';
import { createI18n } from 'vue-i18n';
import staticI18nMsgs from '@intlify/unplugin-vue-i18n/messages';

import App from './App.vue';
import router from './router';

import './assets/main.css';

const i18n = createI18n({
  legacy: false,
  globalInjection: true,
  locale: 'en',
  fallbackLocale: 'en',
  messages: staticI18nMsgs,
});

const app = createApp(App);

app.use(i18n);
app.use(createPinia());
app.use(router);

app.mount('#app');
