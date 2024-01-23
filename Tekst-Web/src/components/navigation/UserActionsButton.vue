<script setup lang="ts">
import { ref, computed, h, type Component } from 'vue';
import { useAuthStore, useStateStore } from '@/stores';
import { type RouteLocationRaw, RouterLink } from 'vue-router';
import { NButton, NIcon, NDropdown } from 'naive-ui';
import { $t } from '@/i18n';
import { useThemeStore } from '@/stores/theme';

import { LogInIcon, LogOutIcon, UserIcon, AdminIcon, ResourceIcon } from '@/icons';

const auth = useAuthStore();
const state = useStateStore();
const theme = useThemeStore();

const tooltip = computed(() =>
  auth.loggedIn
    ? $t('account.tipUserBtn', { username: auth.user?.username })
    : $t('account.tipLoginBtn')
);

const showUserDropdown = ref(false);

const userOptions = computed(() => [
  {
    label: renderLink(() => `${auth.user?.name}`, {
      name: 'account',
    }),
    key: 'account',
    icon: renderIcon(UserIcon),
  },
  {
    label: renderLink(() => $t('resources.heading'), {
      name: 'resources',
      params: {
        text: state.text?.slug || '',
      },
    }),
    key: 'resources',
    icon: renderIcon(ResourceIcon),
  },
  ...(auth.user?.isSuperuser
    ? [
        {
          label: renderLink(() => $t('admin.optionGroupLabel'), {
            name: 'admin',
          }),
          key: 'admin',
          icon: renderIcon(AdminIcon),
        },
      ]
    : []),
  {
    type: 'divider',
    key: 'divider',
  },
  {
    label: $t('account.logoutBtn'),
    key: 'logout',
    icon: renderIcon(LogOutIcon),
  },
]);

function renderLink(
  label: string | (() => string),
  to: RouteLocationRaw,
  props?: Record<string, unknown>
) {
  return () =>
    h(
      RouterLink,
      {
        to,
        ...props,
      },
      { default: label }
    );
}

function renderIcon(icon: Component) {
  return () => h(NIcon, null, { default: () => h(icon) });
}

async function handleLoginClick() {
  auth.showLoginModal();
}

function handleUserOptionSelect(key: string) {
  showUserDropdown.value = false;
  if (key === 'logout') {
    auth.logout();
  }
}
</script>

<template>
  <n-dropdown
    v-if="auth.loggedIn"
    :options="userOptions"
    :size="state.dropdownSize"
    to="#app-container"
    trigger="click"
    @select="handleUserOptionSelect"
  >
    <n-button
      :secondary="!auth.loggedIn"
      circle
      size="large"
      :title="tooltip"
      :focusable="false"
      :color="theme.accentColors.base"
      style="color: #fff"
      class="user-options-button"
    >
      <template #icon>
        <n-icon :component="UserIcon" />
      </template>
    </n-button>
  </n-dropdown>

  <n-button
    v-else
    secondary
    circle
    size="large"
    :title="tooltip"
    :focusable="false"
    class="user-options-button"
    @click="handleLoginClick"
  >
    <template #icon>
      <n-icon :component="LogInIcon" />
    </template>
  </n-button>
</template>

<style scoped>
.user-options-button {
  font-size: var(--app-ui-font-size-mini) !important;
  font-weight: var(--app-ui-font-weight-normal) !important;
}
</style>
