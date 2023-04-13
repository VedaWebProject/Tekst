<script setup lang="ts">
import { RouterView } from 'vue-router';
import FullScreenLoader from '@/components/FullScreenLoader.vue';
import GlobalMessenger from '@/components/GlobalMessenger.vue';
import { computed } from 'vue';
import { localeProfiles } from '@/i18n';
import { useStateStore } from '@/stores';
import { NConfigProvider, NGlobalStyle, NBackTop, lightTheme, darkTheme } from 'naive-ui';
import { getOverrides } from '@/theme';
import PageHeader from './layout/PageHeader.vue';
import PageFooter from './layout/PageFooter.vue';
import { useInitializeApp } from '@/init';

const state = useStateStore();
const { initialized, error } = useInitializeApp();

// i18n
const nUiLangLocale = computed(() => localeProfiles[state.locale].nUiLangLocale);
const nUiDateLocale = computed(() => localeProfiles[state.locale].nUiDateLocale);

// theming
const theme = computed(() => (state.theme === 'light' ? lightTheme : darkTheme));
const themeOverrides = computed(() => getOverrides(state.theme, state.accentColors.base));
const mainBgColor = computed(() => (state.theme === 'light' ? '#00000010' : '#ffffff10'));
const contentBgColor = computed(() => (state.theme === 'light' ? '#ffffffcc' : '#00000044'));
</script>

<template>
  <n-config-provider
    :theme="theme"
    :theme-overrides="themeOverrides"
    :locale="nUiLangLocale"
    :date-locale="nUiDateLocale"
  >
    <div id="app-container">
      <template v-if="error"> ERROR </template>

      <template v-else-if="initialized">
        <PageHeader />
        <main>
          <div id="main-content">
            <RouterView />
          </div>
        </main>
        <PageFooter />
      </template>

      <FullScreenLoader
        :show="state.globalLoading"
        transition="0.2s"
        :text="state.globalLoadingMsg"
        :progress="state.globalLoadingProgress"
        :progress-color="state.accentColors.base"
        show-progress
      />
      <GlobalMessenger />
    </div>
    <n-back-top :visibility-height="200" />
    <n-global-style />
  </n-config-provider>
</template>

<style scoped>
#app-container {
  --accent-color: v-bind(state.accentColors.base);
  --accent-color-fade1: v-bind(state.accentColors.fade1);
  --accent-color-fade2: v-bind(state.accentColors.fade2);
  --accent-color-fade3: v-bind(state.accentColors.fade3);
  --accent-color-fade4: v-bind(state.accentColors.fade4);
  --accent-color-fade5: v-bind(state.accentColors.fade5);

  --link-color: v-bind(state.accentColors.base);
  --link-color-hover: v-bind(state.accentColors.fade1);

  --main-bg-color: v-bind(mainBgColor);
  --content-bg-color: v-bind(contentBgColor);
}

main {
  background-color: var(--main-bg-color);
  box-shadow: inset 0 12px 12px -12px rgba(0, 0, 0, 0.4),
    inset 0 -10px 12px -12px rgba(0, 0, 0, 0.1);
}

#main-content {
  width: auto;
  max-width: var(--max-app-width);
  margin: 0 auto;
  padding: var(--layout-padding);
}
</style>

<style>
a,
a:any-link {
  color: var(--link-color);
}

a:hover {
  color: var(--link-color-hover);
}
</style>
