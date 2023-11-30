<script setup lang="ts">
import { RouterView } from 'vue-router';
import FullScreenLoader from '@/components/FullScreenLoader.vue';
import GlobalMessenger from '@/components/GlobalMessenger.vue';
import { computed } from 'vue';
import { localeProfiles } from '@/i18n';
import { useStateStore } from '@/stores';
import { NConfigProvider, NDialogProvider, NGlobalStyle, NBackTop, useThemeVars } from 'naive-ui';
import { useTheme } from '@/theme';
import PageHeader from './layout/PageHeader.vue';
import PageFooter from './layout/PageFooter.vue';
import { useInitializeApp } from '@/init';
import LoginModal from '@/components/LoginModal.vue';
import HugeLabeledIcon from '@/components/HugeLabeledIcon.vue';
import ErrorTwotone from '@vicons/material/ErrorTwotone';

const state = useStateStore();
const themeVars = useThemeVars();
const { initialized, error } = useInitializeApp();
const { theme, themeOverrides, mainBgColor, contentBgColor, accentColors } = useTheme();

// i18n
const nUiLangLocale = computed(() => localeProfiles[state.locale].nUiLangLocale);
const nUiDateLocale = computed(() => localeProfiles[state.locale].nUiDateLocale);
</script>

<template>
  <n-config-provider
    :theme="theme"
    :theme-overrides="themeOverrides"
    :locale="nUiLangLocale"
    :date-locale="nUiDateLocale"
  >
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

        <FullScreenLoader
          :show="state.globalLoading"
          transition="0.2s"
          :text="state.globalLoadingMsg"
          :progress="state.globalLoadingProgress"
          :progress-color="accentColors.base"
          show-progress
        />
        <GlobalMessenger />
      </div>
      <LoginModal />
      <n-back-top :visibility-height="200" />
      <n-global-style />
    </n-dialog-provider>
  </n-config-provider>
</template>

<style scoped>
#app-container {
  --accent-color: v-bind(accentColors.base);
  --accent-color-fade1: v-bind(accentColors.fade1);
  --accent-color-fade2: v-bind(accentColors.fade2);
  --accent-color-fade3: v-bind(accentColors.fade3);
  --accent-color-fade4: v-bind(accentColors.fade4);
  --accent-color-fade5: v-bind(accentColors.fade5);
  --accent-color-inverted: v-bind(accentColors.inverted);
  --accent-color-inverted-pastel: v-bind(accentColors.invertedPastel);
  --accent-color-inverted-dark: v-bind(accentColors.invertedDark);

  --link-color: v-bind(accentColors.base);
  --link-color-hover: v-bind(accentColors.fade1);

  --main-bg-color: v-bind(mainBgColor);
  --content-bg-color: v-bind(contentBgColor);
  --text-color: v-bind(themeVars.textColor3);

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
