<script setup lang="ts">
import { RouterView } from 'vue-router';
import FullScreenLoader from '@/components/FullScreenLoader.vue';
import GlobalMessenger from '@/components/GlobalMessenger.vue';
import { onMounted, onBeforeMount, ref, computed } from 'vue';
import { LANGUAGES as LANGS } from '@/i18n';
import { useStateStore, useUiDataStore, useMessagesStore, useSettingsStore } from '@/stores';
import { NConfigProvider, NGlobalStyle, lightTheme, darkTheme } from 'naive-ui';
import { lightOverrides, darkOverrides } from '@/theme';
import PageHeader from './layout/PageHeader.vue';
import PageFooter from './layout/PageFooter.vue';
import { i18n } from '@/i18n';

const state = useStateStore();
const settings = useSettingsStore();
const messages = useMessagesStore();
const ui = useUiDataStore();

const loaderText = ref('');
const loaderShowSpinner = ref(true);
const initLoadingFinished = ref(false);

const nUiLangLocale = computed(() => LANGS[settings.language].nUiLangLocale);
const nUiDateLocale = computed(() => LANGS[settings.language].nUiDateLocale);

onBeforeMount(() => {
  state.startGlobalLoading();
});

onMounted(async () => {
  let err = false;

  // TODO: instead of just i18n, all resources needed for bootstrapping the
  // client should be loaded from the server here...
  loaderText.value = i18n.global.t('loading.serverI18n');
  await settings.setLanguage().catch(() => {
    messages.warning(i18n.global.t('errors.serverI18n'));
    // console.error(e);
    err = true;
  });

  loaderText.value = i18n.global.t('loading.uiData');
  await ui.loadUiData().catch(() => {
    messages.warning(i18n.global.t('errors.uiData'));
    // console.error(e);
    err = true;
  });

  err && messages.error(i18n.global.t('errors.appInit'));
  loaderText.value = i18n.global.t('loading.ready');
  initLoadingFinished.value = true;
  state.finishGlobalLoading(200);
});
</script>

<template>
  <n-config-provider
    :theme="settings.theme === 'light' ? lightTheme : darkTheme"
    :theme-overrides="settings.theme === 'light' ? lightOverrides : darkOverrides"
    :locale="nUiLangLocale"
    :date-locale="nUiDateLocale"
  >
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
    <n-global-style />
  </n-config-provider>
</template>

<style scoped>
main {
  border: 1px dashed #0000ff;
  padding: 0.8em;
}
</style>
