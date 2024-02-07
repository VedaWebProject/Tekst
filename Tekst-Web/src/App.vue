<script setup lang="ts">
import { RouterView } from 'vue-router';
import InitLoader from '@/components/InitLoader.vue';
import GlobalMessenger from '@/components/messages/GlobalMessenger.vue';
import { computed } from 'vue';
import { getLocaleProfile } from '@/i18n';
import { useStateStore } from '@/stores';
import {
  NLoadingBarProvider,
  NConfigProvider,
  NDialogProvider,
  NGlobalStyle,
  NBackTop,
  useThemeVars,
} from 'naive-ui';
import { useThemeStore } from '@/stores/theme';
import PageHeader from './layout/PageHeader.vue';
import PageFooter from './layout/PageFooter.vue';
import { useInitializeApp } from '@/composables/init';
import LoginModal from '@/components/modals/LoginModal.vue';
import HugeLabelledIcon from '@/components/generic/HugeLabelledIcon.vue';

import { ErrorIcon } from '@/icons';

const state = useStateStore();
const theme = useThemeStore();
const themeVars = useThemeVars();
const { initialized, error } = useInitializeApp();

// i18n
const nUiLangLocale = computed(() => getLocaleProfile(state.locale)?.nUiLangLocale);
const nUiDateLocale = computed(() => getLocaleProfile(state.locale)?.nUiDateLocale);
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
          <huge-labelled-icon
            v-if="initialized && error"
            :message="$t('init.error')"
            :loading="!error && !initialized"
            :icon="ErrorIcon"
          />

          <template v-else-if="initialized">
            <page-header />
            <main>
              <div id="main-content">
                <router-view />
              </div>
            </main>
            <page-footer />
          </template>

          <init-loader
            :show="state.initLoading"
            transition="0.2s"
            :text="state.initLoadingMsg"
            :dark-mode="theme.darkMode"
          />
          <global-messenger />
        </div>
        <login-modal />
        <n-back-top :visibility-height="200" style="z-index: 2" />
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
  padding: var(--layout-gap) 0;
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
