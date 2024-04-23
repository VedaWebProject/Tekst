<script setup lang="ts">
import { NDrawer, NDrawerContent } from 'naive-ui';
import { computed } from 'vue';
import NavigationMenu from '@/components/navigation/NavigationMenu.vue';
import ThemeModeSwitcher from '@/components/navigation/ThemeModeSwitcher.vue';
import LocaleSwitcher from '@/components/navigation/LocaleSwitcher.vue';
import UserActionsButton from '@/components/navigation/UserActionsButton.vue';
import QuickSearchWidget from '@/components/navigation/QuickSearch.vue';
import HelpNavButton from '@/components/navigation/HelpNavButton.vue';
import {
  useAccountMenuOptions,
  useAdminMenuOptions,
  useMainMenuOptions,
} from '@/components/navigation/navMenuOptions';
import { $t } from '@/i18n';
import { useAuthStore } from '@/stores';

withDefaults(
  defineProps<{
    showUserActionsButton?: boolean;
  }>(),
  {
    showUserActionsButton: false,
  }
);

const show = defineModel<boolean>('show');

const auth = useAuthStore();
const { menuOptions: mainMenuOptions } = useMainMenuOptions();
const { menuOptions: accountMenuOptions } = useAccountMenuOptions();
const { menuOptions: adminMenuOptions } = useAdminMenuOptions();

const allMenuOptions = computed(() => [
  {
    type: 'group',
    key: 'general-group',
    label: $t('general.platform'),
    children: mainMenuOptions.value
      .concat(mainMenuOptions.value.find((o) => o.key === 'info')?.children || [])
      .filter((o) => o.key !== 'info'),
  },
  ...(auth.loggedIn
    ? [
        {
          type: 'group',
          key: 'account-group',
          label: auth.user?.name || auth.user?.username,
          children: accountMenuOptions,
        },
      ]
    : []),
  ...(auth.loggedIn && auth.user?.isSuperuser
    ? [
        {
          type: 'group',
          key: 'admin-group',
          label: $t('admin.heading'),
          children: adminMenuOptions.value,
        },
      ]
    : []),
]);
</script>

<template>
  <n-drawer v-model:show="show" :width="600" :auto-focus="false" style="max-width: 90%">
    <n-drawer-content closable header-style="background-color: var(--accent-color-fade5);">
      <template #header>
        <div class="header-buttons">
          <quick-search-widget />
          <theme-mode-switcher />
          <locale-switcher />
          <help-nav-button />
          <user-actions-button v-if="showUserActionsButton" />
        </div>
      </template>
      <navigation-menu mode="vertical" :options="allMenuOptions" />
    </n-drawer-content>
  </n-drawer>
</template>

<style scoped>
.header-buttons {
  display: flex;
  align-items: center;
  justify-content: space-around;
  gap: 4px;
  width: 60%;
  max-width: 80vw;
  margin: 0 auto;
}
</style>
