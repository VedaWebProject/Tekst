<script setup lang="ts">
import { RouterView } from 'vue-router';
import FullScreenLoader from '@/components/FullScreenLoader.vue';
import GlobalMessenger from '@/components/GlobalMessenger.vue';
import { onMounted, onBeforeMount, ref, computed } from 'vue';
import { languageProfiles } from '@/i18n';
import { useStateStore, usePlatformStore, useMessagesStore, useSettingsStore } from '@/stores';
import { NConfigProvider, NGlobalStyle, lightTheme, darkTheme, useThemeVars } from 'naive-ui';
import { lightOverrides, darkOverrides } from '@/theme';
import PageHeader from './layout/PageHeader.vue';
import PageFooter from './layout/PageFooter.vue';
import { useI18n } from 'vue-i18n';

const state = useStateStore();
const settings = useSettingsStore();
const messages = useMessagesStore();
const pf = usePlatformStore();
const themeVars = useThemeVars();

// i18n
const { t } = useI18n({ useScope: 'global' });
const nUiLangLocale = computed(() => languageProfiles[settings.language].nUiLangLocale);
const nUiDateLocale = computed(() => languageProfiles[settings.language].nUiDateLocale);

// theming
const theme = computed(() => (settings.theme === 'light' ? lightTheme : darkTheme));
const themeOverrides = computed(() =>
  settings.theme === 'light' ? lightOverrides : darkOverrides
);
const mainBgColor = computed(() => (settings.theme === 'light' ? '#00000010' : '#ffffff10'));
const contentBgColor = computed(() => (settings.theme === 'light' ? '#ffffffcc' : '#00000044'));

// app initialization
const appInitialized = ref(false);
const initSteps = [
  {
    info: t('loading.serverI18n'),
    action: async () => {
      try {
        await settings.setLanguage();
        return true;
      } catch (e) {
        messages.warning(t('errors.serverI18n'));
        console.error(e);
        return false;
      }
    },
  },
  {
    info: t('loading.platformData'),
    action: async () => {
      try {
        await pf.loadPlatformData();
        return true;
      } catch (e) {
        messages.warning(t('errors.platformData'));
        console.error(e);
        return false;
      }
    },
  },
];

onBeforeMount(() => {
  state.startGlobalLoading();
});

onMounted(async () => {
  let err = false;
  let count = 0;

  for (const step of initSteps) {
    state.globalLoadingProgress = count / initSteps.length;
    state.globalLoadingMsg = step.info;
    const success = await step.action();
    err = err || !success;
    count++;
    state.globalLoadingProgress = count / initSteps.length;
  }

  err && messages.error(t('errors.appInit'));
  state.globalLoadingMsg = t('loading.ready');
  state.setPageTitle();
  appInitialized.value = true;
  await state.finishGlobalLoading(200, 200);
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
      <template v-if="appInitialized">
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
        :progress-color="state.accentColor.intense"
        show-progress
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

  --link-color: v-bind(themeVars.primaryColor);
  --link-color-hover: v-bind(themeVars.primaryColorHover);

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
  padding: var(--layout-padding) 0.5rem;
}
</style>
