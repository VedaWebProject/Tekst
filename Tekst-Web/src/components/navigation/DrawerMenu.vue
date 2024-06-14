<script setup lang="ts">
import { NFlex, NDrawer, NDrawerContent } from 'naive-ui';
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
    children: mainMenuOptions.value.filter((o) => o.key !== 'info'),
  },
  ...(mainMenuOptions.value.find((o) => o.key === 'info')?.children?.length
    ? [
        {
          type: 'group',
          key: 'info-group',
          label: mainMenuOptions.value.find((o) => o.key === 'info')?.label,
          children: mainMenuOptions.value.find((o) => o.key === 'info')?.children,
        },
      ]
    : []),
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
    <n-drawer-content closable>
      <template #header>
        <n-flex justify="center">
          <quick-search-widget />
          <theme-mode-switcher @click="show = false" />
          <locale-switcher />
          <help-nav-button @click="show = false" />
          <user-actions-button v-if="showUserActionsButton && !auth.loggedIn" />
        </n-flex>
      </template>
      <navigation-menu mode="vertical" :options="allMenuOptions" @select="() => (show = false)" />
    </n-drawer-content>
  </n-drawer>
</template>
