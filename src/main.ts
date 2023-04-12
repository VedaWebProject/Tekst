import { createApp } from 'vue';
import { createPinia } from 'pinia';
import { i18n } from '@/i18n';

import App from '@/App.vue';
import router from '@/router';

import 'normalize.css';
import '@/assets/main.css';

const app = createApp(App);

app.use(router);
app.use(i18n);
app.use(createPinia());

app.mount('#app');
