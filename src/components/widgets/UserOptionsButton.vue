<script setup lang="ts">
import { ref, computed, h, type Component } from 'vue';
import { useAuthStore, useStateStore } from '@/stores';
import { useRouter } from 'vue-router';
import { NButton, NIcon, NDropdown } from 'naive-ui';
import { useI18n } from 'vue-i18n';

import LogInRound from '@vicons/material/LogInRound';
import LogOutRound from '@vicons/material/LogOutRound';
import SettingsRound from '@vicons/material/SettingsRound';
import PersonRound from '@vicons/material/PersonRound';
import RemoveRedEyeRound from '@vicons/material/RemoveRedEyeRound';

const { t } = useI18n({ useScope: 'global' });
const auth = useAuthStore();
const state = useStateStore();
const router = useRouter();
const tooltip = computed(() =>
  auth.loggedIn ? t('user.tipUserBtn', { username: auth.user?.username }) : t('user.tipLoginBtn')
);

const showUserDropdown = ref(false);

const userOptions = computed(() => [
  {
    type: 'group',
    label: `${auth.user?.firstName} ${auth.user?.lastName} (${auth.user?.username})`,
    key: 'user',
    children: [
      {
        label: t('user.profile'),
        key: 'profile',
        icon: renderIcon(RemoveRedEyeRound),
      },
      {
        label: t('user.account.optionLabel'),
        key: 'account',
        icon: renderIcon(PersonRound),
      },
    ],
  },
  ...(auth.user?.isSuperuser
    ? [
        {
          type: 'divider',
          key: 'dividerAdministration',
        },
      ]
    : []),
  ...(auth.user?.isSuperuser
    ? [
        {
          label: t('administration.optionLabel'),
          key: 'admin',
          icon: renderIcon(SettingsRound),
        },
      ]
    : []),
  {
    type: 'divider',
    key: 'dividerLogout',
  },
  {
    label: t('user.logout'),
    key: 'logout',
    icon: renderIcon(LogOutRound),
  },
]);

const initials = computed(
  () =>
    auth.loggedIn &&
    `${auth.user?.firstName[0].toUpperCase()}${auth.user?.lastName[0].toUpperCase()}`
);

const color = computed(() => (auth.loggedIn ? state.accentColors.fade2 : undefined));

function renderIcon(icon: Component) {
  return () => h(NIcon, null, { default: () => h(icon) });
}

function handleClick() {
  if (!auth.loggedIn) {
    router.push({ name: 'login' });
  } else {
    showUserDropdown.value = !showUserDropdown.value;
  }
}

function handleUserOptionSelect(option: string) {
  showUserDropdown.value = false;
  switch (option) {
    case 'profile':
      router.push({ name: 'user', params: { username: auth.user?.username } });
      break;
    case 'account':
      router.push({ name: 'accountManage' });
      break;
    case 'logout':
      auth.logout();
      break;
    case 'admin':
      router.push({ name: 'adminOverview' });
      break;
  }
}
</script>

<template>
  <n-dropdown
    :show="showUserDropdown"
    :options="userOptions"
    :on-clickoutside="() => (showUserDropdown = false)"
    :size="state.dropdownSize"
    @select="handleUserOptionSelect"
  >
    <n-button
      :secondary="!auth.loggedIn"
      circle
      size="large"
      @click="handleClick"
      :title="tooltip"
      :focusable="false"
      :color="color"
      :style="auth.loggedIn && 'color: #fff'"
      class="user-options-button"
    >
      <template v-if="auth.loggedIn">{{ initials }}</template>
      <template v-if="!auth.loggedIn" #icon>
        <n-icon :component="LogInRound" />
      </template>
    </n-button>
  </n-dropdown>
</template>

<style scoped>
.user-options-button {
  font-size: var(--app-ui-font-size-mini) !important;
  font-weight: var(--app-ui-font-weight-normal) !important;
}
</style>

<style scoped>
.user-options-button {
  font-size: var(--app-ui-font-size-mini) !important;
  font-weight: var(--app-ui-font-weight-normal) !important;
}
</style>
