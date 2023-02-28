<script setup lang="ts">
import { RouterView, useRoute } from 'vue-router';
import FullScreenLoader from '@/components/FullScreenLoader.vue';
import GlobalMessenger from '@/components/GlobalMessenger.vue';
import { onMounted, onBeforeMount, ref, computed } from 'vue';
import { LANGUAGES as LANGS } from '@/i18n';
import { useStateStore, usePlatformStore, useMessagesStore, useSettingsStore } from '@/stores';
import { NConfigProvider, NGlobalStyle, lightTheme, darkTheme } from 'naive-ui';
import { lightOverrides, darkOverrides } from '@/theme';
import PageHeader from './layout/PageHeader.vue';
import PageFooter from './layout/PageFooter.vue';
import { i18n } from '@/i18n';
import { setPageTitle } from './router';

const state = useStateStore();
const settings = useSettingsStore();
const messages = useMessagesStore();
const pf = usePlatformStore();

const t = i18n.global.t;
const route = useRoute();
const appInitialized = ref(false);

const nUiLangLocale = computed(() => LANGS[settings.language].nUiLangLocale);
const nUiDateLocale = computed(() => LANGS[settings.language].nUiDateLocale);

const theme = computed(() => (settings.theme === 'light' ? lightTheme : darkTheme));
const themeOverrides = computed(() =>
  settings.theme === 'light' ? lightOverrides : darkOverrides
);

interface InitStep {
  info: string;
  action: () => Promise<boolean>;
}

const initSteps: InitStep[] = [
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
  setPageTitle(route);
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
          <RouterView />
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

  max-width: 100%;
  font-family: Assistant;
}

main {
  max-width: var(--max-app-width);
  margin: 0 auto;
  padding: 1em;
}
</style>
