<script setup lang="ts">
import { RouterView } from 'vue-router';
import InitLoader from '@/components/InitLoader.vue';
import GlobalMessenger from '@/components/GlobalMessenger.vue';
import { computed } from 'vue';
import { localeProfiles } from '@/i18n';
import { useStateStore } from '@/stores';
import {
  NLoadingBarProvider,
  NConfigProvider,
  NDialogProvider,
  NGlobalStyle,
  NBackTop,
  useThemeVars,
} from 'naive-ui';
import { useThemeStore } from '@/theme';
import PageHeader from './layout/PageHeader.vue';
import PageFooter from './layout/PageFooter.vue';
import { useInitializeApp } from '@/init';
import LoginModal from '@/components/LoginModal.vue';
import HugeLabeledIcon from '@/components/HugeLabeledIcon.vue';
import ErrorTwotone from '@vicons/material/ErrorTwotone';

const state = useStateStore();
const theme = useThemeStore();
const themeVars = useThemeVars();
const { initialized, error } = useInitializeApp();

// i18n
const nUiLangLocale = computed(() => localeProfiles[state.locale].nUiLangLocale);
const nUiDateLocale = computed(() => localeProfiles[state.locale].nUiDateLocale);
</script>

<template>
  <n-config-provider
    :theme="theme.theme"
    :theme-overrides="theme.overrides"
    :locale="nUiLangLocale"
    :date-locale="nUiDateLocale"
  >
    <n-loading-bar-provider>
      <n-dialog-provider>
        <div id="app-container">
          <HugeLabeledIcon
            v-if="initialized && error"
            :message="$t('init.error')"
            :loading="!error && !initialized"
            :icon="ErrorTwotone"
          />

          <template v-else-if="initialized">
            <PageHeader />
            <main>
              <div id="main-content">
                <RouterView />
              </div>
            </main>
            <PageFooter />
          </template>

          <InitLoader
            :show="state.initLoading"
            transition="0.2s"
            :text="state.initLoadingMsg"
            :dark-mode="theme.darkMode"
          />
          <GlobalMessenger />
        </div>
        <LoginModal />
        <n-back-top :visibility-height="200" />
        <n-global-style />
      </n-dialog-provider>
    </n-loading-bar-provider>
  </n-config-provider>
</template>

<style scoped>
#app-container {
  --accent-color: v-bind(theme.accentColors.base);
  --accent-color-fade1: v-bind(theme.accentColors.fade1);
  --accent-color-fade2: v-bind(theme.accentColors.fade2);
  --accent-color-fade3: v-bind(theme.accentColors.fade3);
  --accent-color-fade4: v-bind(theme.accentColors.fade4);
  --accent-color-fade5: v-bind(theme.accentColors.fade5);
  --accent-color-inverted: v-bind(theme.accentColors.inverted);
  --accent-color-inverted-pastel: v-bind(theme.accentColors.invertedPastel);
  --accent-color-inverted-dark: v-bind(theme.accentColors.invertedDark);

  --link-color: v-bind(theme.accentColors.base);
  --link-color-hover: v-bind(theme.accentColors.fade1);

  --main-bg-color: v-bind(theme.mainBgColor);
  --content-bg-color: v-bind(theme.contentBgColor);
  --text-color: v-bind(themeVars.textColor1);
  --text-color-fade: v-bind(themeVars.textColor3);

  /* NaiveUI feedback colors */
  --col-info: v-bind(themeVars.infoColor);
  --col-success: v-bind(themeVars.successColor);
  --col-warning: v-bind(themeVars.warningColor);
  --col-error: v-bind(themeVars.errorColor);
}

main {
  background-color: var(--main-bg-color);
  box-shadow:
    inset 0 12px 12px -12px rgba(0, 0, 0, 0.4),
    inset 0 -10px 12px -12px rgba(0, 0, 0, 0.1);
}

#main-content {
  width: auto;
  max-width: var(--max-app-width);
  margin: 0 auto;
  padding: var(--layout-gap);
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
