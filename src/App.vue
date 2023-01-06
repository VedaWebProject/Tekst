<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router';
import FullScreenLoader from '@/components/FullScreenLoader.vue';
import LanguageSwitcher from '@/i18n/LanguageSwitcher.vue';
import ThemeModeSwitcher from '@/i18n/ThemeModeSwitcher.vue';
import { onMounted, onBeforeMount } from 'vue';
import { useAppStateStore } from '@/stores/general';
import { NConfigProvider, NGlobalStyle, NSpace, lightTheme, darkTheme } from 'naive-ui';
import { useSettingsStore } from '@/stores/settings';
import { lightOverrides, darkOverrides } from '@/theme';

const appState = useAppStateStore();
const settings = useSettingsStore();

onBeforeMount(() => {
  appState.startGlobalLoading();
});

onMounted(() => {
  // TODO: instead of just i18n, all resources needed for bootstrapping the
  // client should be loaded from the server here...
  settings
    .setLanguage()
    .then(() => {
      appState.finishGlobalLoading();
    })
    .catch((error) => {
      console.error(error);
      // TODO: Give error feedback...
    });
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
    <FullScreenLoader :show="appState.globalLoading" duration="100ms" text="loading..." />
    <n-global-style />
  </n-config-provider>
</template>

<style scoped></style>
