import { createApp } from 'vue';
import { createPinia } from 'pinia';
import { setupI18n } from './i18n';

import App from './App.vue';
import router from './router';

import './assets/main.css';

const app = createApp(App);

app.use(setupI18n());
app.use(createPinia());
app.use(router);

app.mount('#app');
