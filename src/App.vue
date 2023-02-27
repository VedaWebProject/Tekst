<script setup lang="ts">
import { RouterView, useRoute } from 'vue-router';
import FullScreenLoader from '@/components/FullScreenLoader.vue';
import GlobalMessenger from '@/components/GlobalMessenger.vue';
import { onMounted, onBeforeMount, ref, computed } from 'vue';
import { LANGUAGES as LANGS } from '@/i18n';
import { useStateStore, usePlatformStore, useMessagesStore, useSettingsStore } from '@/stores';
import { NConfigProvider, NGlobalStyle, lightTheme, darkTheme, useThemeVars } from 'naive-ui';
import { lightOverrides, darkOverrides } from '@/theme';
import PageHeader from './layout/PageHeader.vue';
import PageFooter from './layout/PageFooter.vue';
import { i18n } from '@/i18n';
import Color from 'color';
import { setPageTitle } from './router';

const state = useStateStore();
const settings = useSettingsStore();
const messages = useMessagesStore();
const pf = usePlatformStore();

const t = i18n.global.t;
const route = useRoute();
const loaderText = ref('');
const loaderShowSpinner = ref(true);
const initLoadingFinished = ref(false);

const nUiLangLocale = computed(() => LANGS[settings.language].nUiLangLocale);
const nUiDateLocale = computed(() => LANGS[settings.language].nUiDateLocale);

const themeVars = useThemeVars();
const theme = computed(() => (settings.theme === 'light' ? lightTheme : darkTheme));
const themeOverrides = computed(() =>
  settings.theme === 'light' ? lightOverrides : darkOverrides
);

const textColor = computed(() => themeVars.value.textColorBase);
const textColorInverted = computed(() => Color(textColor.value).negate().hex());

onBeforeMount(() => {
  state.startGlobalLoading();
});

onMounted(async () => {
  let err = false;

  // TODO: instead of just i18n, all resources needed for bootstrapping the
  // client should be loaded from the server here...
  loaderText.value = t('loading.serverI18n');
  await settings.setLanguage().catch(() => {
    messages.warning(t('errors.serverI18n'));
    // console.error(e);
    err = true;
  });

  loaderText.value = t('loading.platformData');
  await pf.loadPlatformData().catch((e) => {
    messages.warning(t('errors.platformData'));
    console.error(e);
    err = true;
  });

  err && messages.error(t('errors.appInit'));
  loaderText.value = t('loading.ready');
  initLoadingFinished.value = true;
  setPageTitle(route);
  state.finishGlobalLoading(200);
});
</script>

<template>
  <n-config-provider
    :theme="theme"
    :theme-overrides="themeOverrides"
    :locale="nUiLangLocale"
    :date-locale="nUiDateLocale"
  >
    <div id="app-container">
      <template v-if="initLoadingFinished">
        <PageHeader />
        <main>
          <RouterView />
        </main>
        <PageFooter />
      </template>

      <FullScreenLoader
        :show="state.globalLoading"
        transition="0.2s"
        :text="loaderText"
        :spinner="loaderShowSpinner"
      />
      <GlobalMessenger />
    </div>
    <n-global-style />
  </n-config-provider>
</template>

<style scoped>
#app-container {
  --accent-color: v-bind(state.accentColor.base);
  --accent-color-intense: v-bind(state.accentColor.intense);
  --accent-color-fade1: v-bind(state.accentColor.fade1);
  --accent-color-fade2: v-bind(state.accentColor.fade2);
  --accent-color-fade3: v-bind(state.accentColor.fade3);
  --accent-color-fade4: v-bind(state.accentColor.fade4);
  --accent-color-fade5: v-bind(state.accentColor.fade5);
  --theme-text-color: v-bind(textColor);
  --theme-text-color-inverted: v-bind(textColorInverted);

  max-width: 100%;
  font-family: Assistant;
}

main {
  max-width: var(--max-app-width);
  margin: 0 auto;
  padding: 1em;
}
</style>
