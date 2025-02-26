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
    :theme="theme.nuiBaseTheme"
    :theme-overrides="theme.nuiThemeOverrides"
    :locale="nUiLangLocale"
    :date-locale="nUiDateLocale"
    :class="{dark: theme.dark}"
  >
    <n-loading-bar-provider>
      <n-dialog-provider>
        <!-- app content when initialized -->
        <template v-if="state.init.initialized && !state.init.error">
          <page-header />
          <main>
            <div id="main-content">
              <router-view />
            </div>
          </main>
          <page-footer />
          <login-modal />
          <messaging-modal />
          <tasks-widget v-if="showTasksWidget" />
          <n-back-top
            v-model:show="state.backtopVisible"
            :visibility-height="200"
            style="z-index: 2"
          />
        </template>
        <!-- feedback on app init error -->
        <n-flex
          v-else-if="state.init.initialized && state.init.error"
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
      </n-dialog-provider>
      <app-loading-feedback />
    </n-loading-bar-provider>
    <global-messenger />
    <n-global-style />
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
