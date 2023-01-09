<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router';
import FullScreenLoader from '@/components/FullScreenLoader.vue';
import LanguageSwitcher from '@/i18n/LanguageSwitcher.vue';
import ThemeModeSwitcher from '@/components/ThemeModeSwitcher.vue';
import GlobalMessenger from '@/components/GlobalMessenger.vue';
import { onMounted, onBeforeMount, ref } from 'vue';
import { useAppStateStore } from '@/stores/general';
import { useMessagesStore } from '@/stores/messages';
import { NConfigProvider, NGlobalStyle, NSpace, lightTheme, darkTheme } from 'naive-ui';
import { useSettingsStore } from '@/stores/settings';
import { lightOverrides, darkOverrides } from '@/theme';

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

  appState.finishGlobalLoading();
});
</script>

<template>
  <n-config-provider
    :theme="settings.theme === 'light' ? lightTheme : darkTheme"
    :theme-overrides="settings.theme === 'light' ? lightOverrides : darkOverrides"
  >
    <header>
      <img alt="TextRig Logo" class="logo" src="@/assets/logo.png" width="125" height="125" />

      <div class="wrapper">
        <nav>
          <RouterLink to="/">Home</RouterLink>
          <RouterLink to="/about">About</RouterLink>
        </nav>

        <h2>{{ $t('foo.welcome') }}</h2>
        <n-space inline :wrap-item="false" size="small">
          <LanguageSwitcher size="small" />
          <ThemeModeSwitcher size="small" />
        </n-space>
      </div>
    </header>

    <RouterView />
    <FullScreenLoader
      :show="appState.globalLoading"
      transition="100ms"
      :text="loaderText"
      :spinner="loaderShowSpinner"
    />
    <GlobalMessenger />
    <n-global-style />
  </n-config-provider>
</template>

<style scoped></style>
