<script setup lang="ts">
import { RouterView } from 'vue-router';
import FullScreenLoader from '@/components/FullScreenLoader.vue';
import GlobalMessenger from '@/components/GlobalMessenger.vue';
import { onMounted, onBeforeMount, ref } from 'vue';
import { useAppStateStore } from '@/stores/general';
import { useUiDataStore } from '@/stores/uiData';
import { useMessagesStore } from '@/stores/messages';
import { NConfigProvider, NGlobalStyle, lightTheme, darkTheme } from 'naive-ui';
import { useSettingsStore } from '@/stores/settings';
import { lightOverrides, darkOverrides } from '@/theme';
import PageHeader from './layout/PageHeader.vue';
import PageFooter from './layout/PageFooter.vue';

const appState = useAppStateStore();
const settings = useSettingsStore();
const messages = useMessagesStore();
const ui = useUiDataStore();

const loaderText = ref('');
const loaderShowSpinner = ref(true);
let initLoadingFinished = ref(false);

onBeforeMount(() => {
  appState.startGlobalLoading();
});

onMounted(async () => {
  let err = false;

  // TODO: instead of just i18n, all resources needed for bootstrapping the
  // client should be loaded from the server here...
  loaderText.value = 'Loading server-managed language data...';
  await settings.setLanguage().catch((e) => {
    messages.create({ text: 'Could not load language data from server', type: 'warning' });
    console.error(e);
    err = true;
  });

  loaderText.value = 'Loading instance data...';
  const apiUrl = import.meta.env.TEXTRIG_SERVER_API;
  await fetch(`${apiUrl}/uidata`)
    .then((response) => response.json())
    .then((data) => {
      ui.data = data;
    })
    .catch((e) => {
      messages.create({ text: 'Could not load instance data from server', type: 'warning' });
      console.error(e);
      err = true;
    });

  err &&
    messages.create({
      text: 'There were errors initializing the application',
      type: 'error',
    });
  loaderText.value = 'Ready.';
  appState.finishGlobalLoading(200);
  initLoadingFinished.value = true;
});
</script>

<template>
  <n-config-provider
    :theme="settings.theme === 'light' ? lightTheme : darkTheme"
    :theme-overrides="settings.theme === 'light' ? lightOverrides : darkOverrides"
  >
    <template v-if="initLoadingFinished">
      <PageHeader />
      <main>
        <RouterView />
      </main>
      <PageFooter />
    </template>

    <FullScreenLoader
      :show="appState.globalLoading"
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
  padding: 0.8rem;
}
</style>
