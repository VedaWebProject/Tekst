<script setup lang="ts">
import { RouterView } from 'vue-router';
import FullScreenLoader from '@/components/FullScreenLoader.vue';
import GlobalMessenger from '@/components/GlobalMessenger.vue';
import { onMounted, onBeforeMount, ref, computed } from 'vue';
import { localeProfiles } from '@/i18n';
import { useStateStore, usePlatformStore, useMessagesStore } from '@/stores';
import { NConfigProvider, NGlobalStyle, NBackTop, lightTheme, darkTheme } from 'naive-ui';
import { lightOverrides, darkOverrides } from '@/theme';
import PageHeader from './layout/PageHeader.vue';
import PageFooter from './layout/PageFooter.vue';
import { useI18n } from 'vue-i18n';

const state = useStateStore();
const messages = useMessagesStore();
const pf = usePlatformStore();

// i18n
const { t } = useI18n({ useScope: 'global' });
const nUiLangLocale = computed(() => localeProfiles[state.locale].nUiLangLocale);
const nUiDateLocale = computed(() => localeProfiles[state.locale].nUiDateLocale);

// theming
const theme = computed(() => (state.theme === 'light' ? lightTheme : darkTheme));
const themeOverrides = computed(() => (state.theme === 'light' ? lightOverrides : darkOverrides));
const mainBgColor = computed(() => (state.theme === 'light' ? '#00000010' : '#ffffff10'));
const contentBgColor = computed(() => (state.theme === 'light' ? '#ffffffcc' : '#00000044'));

// app initialization
const appInitialized = ref(false);
const initSteps = [
  {
    info: t('loading.serverI18n'),
    action: async () => {
      try {
        await state.setLocale();
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
  padding: var(--layout-padding) 0.5rem;
}
</style>
