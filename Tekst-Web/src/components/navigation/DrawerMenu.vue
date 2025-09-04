<script setup lang="ts">
import LocaleSwitcher from '@/components/navigation/LocaleSwitcher.vue';
import LogoutButton from '@/components/navigation/LogoutButton.vue';
import NavigationMenu from '@/components/navigation/NavigationMenu.vue';
import {
  useAccountMenuOptions,
  useAdminMenuOptions,
  useMainMenuOptions,
} from '@/components/navigation/navMenuOptions';
import ThemeModeSwitcher from '@/components/navigation/ThemeModeSwitcher.vue';
import UserActionsButton from '@/components/navigation/UserActionsButton.vue';
import { $t } from '@/i18n';
import { useAuthStore, useStateStore } from '@/stores';
import { NDrawer, NDrawerContent, NFlex } from 'naive-ui';
import { computed } from 'vue';

const show = defineModel<boolean>('show');

const auth = useAuthStore();
const state = useStateStore();

const { menuOptions: mainMenuOptions } = useMainMenuOptions();
const { menuOptions: accountMenuOptions } = useAccountMenuOptions();
const { menuOptions: adminMenuOptions } = useAdminMenuOptions();

const allMenuOptions = computed(() => [
  {
    type: 'group',
    key: 'general-group',
    label: state.pf?.state.platformName || $t('common.platform'),
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
  ...(!!auth.user?.isSuperuser
    ? [
        {
          type: 'group',
          key: 'admin-group',
          label: $t('admin.heading'),
          children: adminMenuOptions.value,
        },
      ]
    : []),
  ...(!!auth.user
    ? [
        {
          type: 'group',
          key: 'account-group',
          label: auth.user?.name || auth.user?.username,
          children: accountMenuOptions,
        },
      ]
    : []),
]);
</script>

<template>
  <n-drawer v-model:show="show" :width="600" style="max-width: 90%">
    <n-drawer-content closable>
      <template #header>
        <n-flex :size="32" justify="center" :wrap="false">
          <theme-mode-switcher @click="() => (show = false)" />
          <locale-switcher />
          <user-actions-button v-if="state.pf && !state.pf.security.closedMode && !auth.user" />
          <logout-button v-else-if="!!auth.user" @click="() => (show = false)" />
        </n-flex>
      </template>
      <navigation-menu mode="vertical" :options="allMenuOptions" @select="() => (show = false)" />
    </n-drawer-content>
  </n-drawer>
</template>
