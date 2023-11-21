<script setup lang="ts">
import { ref, computed, h, type Component } from 'vue';
import { useAuthStore, useStateStore } from '@/stores';
import { type RouteLocationRaw, RouterLink } from 'vue-router';
import { NButton, NIcon, NDropdown } from 'naive-ui';
import { $t } from '@/i18n';
import { useTheme } from '@/theme';

import LogInRound from '@vicons/material/LogInRound';
import LogOutRound from '@vicons/material/LogOutRound';
import PersonFilled from '@vicons/material/PersonFilled';
import ShieldOutlined from '@vicons/material/ShieldOutlined';
import LayersFilled from '@vicons/material/LayersFilled';

const auth = useAuthStore();
const state = useStateStore();
const { accentColors } = useTheme();

const tooltip = computed(() =>
  auth.loggedIn
    ? $t('account.tipUserBtn', { username: auth.user?.username })
    : $t('account.tipLoginBtn')
);

const showUserDropdown = ref(false);

const userOptions = computed(() => [
  {
    label: renderLink(() => `${auth.user?.firstName} ${auth.user?.lastName}`, {
      name: 'account',
    }),
    key: 'account',
    icon: renderIcon(PersonFilled),
  },
  {
    label: renderLink(() => $t('dataLayers.heading'), {
      name: 'dataLayers',
      params: {
        text: state.text?.slug || '',
      },
    }),
    key: 'dataLayers',
    icon: renderIcon(LayersFilled),
  },
  ...(auth.user?.isSuperuser
    ? [
        {
          label: renderLink(() => $t('admin.optionGroupLabel'), {
            name: 'admin',
          }),
          key: 'admin',
          icon: renderIcon(ShieldOutlined),
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
    icon: renderIcon(LogOutRound),
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
  auth.showLoginModal(undefined, { name: 'accountProfile' });
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
    trigger="hover"
    @select="handleUserOptionSelect"
  >
    <n-button
      :secondary="!auth.loggedIn"
      circle
      size="large"
      :title="tooltip"
      :focusable="false"
      :color="accentColors.base"
      style="color: #fff"
      class="user-options-button"
    >
      <template #icon>
        <n-icon :component="PersonFilled" />
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
      <n-icon :component="LogInRound" />
    </template>
  </n-button>
</template>

<style scoped>
.user-options-button {
  font-size: var(--app-ui-font-size-mini) !important;
  font-weight: var(--app-ui-font-weight-normal) !important;
}
</style>
