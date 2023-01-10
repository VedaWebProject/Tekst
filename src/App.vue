<script setup lang="ts">
import { RouterView } from 'vue-router';
import FullScreenLoader from '@/components/FullScreenLoader.vue';
import GlobalMessenger from '@/components/GlobalMessenger.vue';
import { onMounted, onBeforeMount, ref } from 'vue';
import { useAppStateStore } from '@/stores/general';
import { useMessagesStore } from '@/stores/messages';
import { NConfigProvider, NGlobalStyle, lightTheme, darkTheme } from 'naive-ui';
import { useSettingsStore } from '@/stores/settings';
import { lightOverrides, darkOverrides } from '@/theme';
import PageHeader from './layout/PageHeader.vue';
import PageFooter from './layout/PageFooter.vue';

const appState = useAppStateStore();
const settings = useSettingsStore();
const messages = useMessagesStore();

const loaderText = ref<string>();
const loaderShowSpinner = ref<boolean>(true);

onBeforeMount(() => {
  appState.startGlobalLoading();
});

onMounted(async () => {
  let errors = false;

  // TODO: instead of just i18n, all resources needed for bootstrapping the
  // client should be loaded from the server here...
  loaderText.value = 'Loading language data...';
  await settings.setLanguage().catch((error) => {
    messages.create({ text: 'Could not load language data from server', type: 'warning' });
    console.error(error);
    errors = true;
  });

  errors &&
    messages.create({
      text: 'There were errors initializing the application',
      type: 'error',
    });
  loaderText.value = 'Ready.';
  appState.finishGlobalLoading(200);
});
</script>

<template>
  <n-config-provider
    :theme="settings.theme === 'light' ? lightTheme : darkTheme"
    :theme-overrides="settings.theme === 'light' ? lightOverrides : darkOverrides"
  >
    <PageHeader />

    <main>
      <RouterView />
    </main>

    <PageFooter />

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
  padding: 0.8rem;
}
</style>
