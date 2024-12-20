import { i18n } from '@/i18n';
import { createPinia } from 'pinia';
import { createApp } from 'vue';

import App from '@/App.vue';
import router from '@/router';

import 'normalize.css';

// commented so the code formatter doesn't rearrange the CSS imports :(
import '@/assets/main.css';

const app = createApp(App);

app.use(i18n);
app.use(createPinia());
app.use(router);

app.mount('#app');
