<script setup lang="ts">
import AppLoadingFeedback from '@/components/AppLoadingFeedback.vue';
import HugeLabelledIcon from '@/components/generic/HugeLabelledIcon.vue';
import GlobalMessenger from '@/components/messages/GlobalMessenger.vue';
import LoginModal from '@/components/modals/LoginModal.vue';
import TasksWidget from '@/components/TasksWidget.vue';
import MessagingModal from '@/components/userMessages/MessagingModal.vue';
import { useFavicon } from '@/composables/favicon';
import { useInitializeApp } from '@/composables/init';
import { useTasks } from '@/composables/tasks';
import { getLocaleProfile } from '@/i18n';
import { ErrorIcon } from '@/icons';
import PageFooter from '@/layout/PageFooter.vue';
import PageHeader from '@/layout/PageHeader.vue';
import { useStateStore, useThemeStore } from '@/stores';
import {
  NBackTop,
  NConfigProvider,
  NDialogProvider,
  NFlex,
  NGlobalStyle,
  NLoadingBarProvider,
} from 'naive-ui';
import { computed } from 'vue';
import { RouterView } from 'vue-router';

const state = useStateStore();
const theme = useThemeStore();
const { showTasksWidget } = useTasks();

useInitializeApp();

// i18n
const nUiLangLocale = computed(() => getLocaleProfile(state.locale)?.nUiLangLocale);
const nUiDateLocale = computed(() => getLocaleProfile(state.locale)?.nUiDateLocale);

// favicon
useFavicon();
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
          <n-flex
            v-if="state.init.initialized && state.init.error"
            justify="center"
            align="center"
            style="height: 100vh"
          >
            <huge-labelled-icon
              :message="$t('init.error')"
              :loading="!state.init.error && !state.init.initialized"
              :icon="ErrorIcon"
            />
          </n-flex>

          <template v-else-if="state.init.initialized">
            <page-header />
            <main>
              <div id="main-content">
                <router-view />
              </div>
            </main>
            <page-footer />
          </template>

          <app-loading-feedback />
          <global-messenger />
          <tasks-widget v-if="showTasksWidget" />
        </div>
        <messaging-modal />
        <login-modal />
        <n-back-top
          v-model:show="state.backtopVisible"
          :visibility-height="200"
          style="z-index: 2"
        />
        <n-global-style />
      </n-dialog-provider>
    </n-loading-bar-provider>
  </n-config-provider>
</template>

<style scoped>
main {
  padding: var(--gap-lg) 0;
  background-color: var(--main-bg-color);
  box-shadow:
    inset 0 12px 12px -12px rgba(0, 0, 0, 0.4),
    inset 0 -10px 12px -12px rgba(0, 0, 0, 0.1);
}

#main-content {
  width: auto;
  max-width: var(--max-app-width);
  margin: 0 auto;
  padding: var(--gap-md);
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

#app-container {
  --accent-color: v-bind(theme.accentColors.base);
  --accent-color-fade1: v-bind(theme.accentColors.fade1);
  --accent-color-fade2: v-bind(theme.accentColors.fade2);
  --accent-color-fade3: v-bind(theme.accentColors.fade3);
  --accent-color-fade4: v-bind(theme.accentColors.fade4);
  --accent-color-fade5: v-bind(theme.accentColors.fade5);
  --accent-color-spotlight: v-bind(theme.accentColors.spotlight);

  --link-color: v-bind(theme.accentColors.base);
  --link-color-hover: v-bind(theme.accentColors.fade1);

  --main-bg-color: v-bind(theme.mainBgColor);
  --content-bg-color: v-bind(theme.contentBgColor);
  --base-color: v-bind(theme.theme.common.baseColor);
  --text-color: v-bind(theme.theme.common.textColor1);
  --text-color-fade: v-bind(theme.theme.common.textColor3);

  /* NaiveUI feedback colors */
  --col-info: v-bind(theme.theme.common.infoColor);
  --col-success: v-bind(theme.theme.common.successColor);
  --col-warning: v-bind(theme.theme.common.warningColor);
  --col-error: v-bind(theme.theme.common.errorColor);
}
</style>
