<script setup lang="ts">
import { ref, computed, h, type Component } from 'vue';
import { useAuthStore, useStateStore } from '@/stores';
import { useRouter, type RouteLocationRaw, RouterLink } from 'vue-router';
import { NButton, NIcon, NDropdown } from 'naive-ui';
import { $t } from '@/i18n';
import { useTheme } from '@/theme';

import LogInRound from '@vicons/material/LogInRound';
import LogOutRound from '@vicons/material/LogOutRound';
import PersonRound from '@vicons/material/PersonRound';
import ShieldOutlined from '@vicons/material/ShieldOutlined';
import LayersFilled from '@vicons/material/LayersFilled';

const auth = useAuthStore();
const state = useStateStore();
const { accentColors } = useTheme();
const router = useRouter();

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
    icon: renderIcon(PersonRound),
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

const color = computed(() => (auth.loggedIn ? accentColors.value.base : undefined));

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
        style: {
          fontSize: 'var(--app-ui-font-size)',
        },
        ...props,
      },
      { default: label }
    );
}

function renderIcon(icon: Component) {
  return () => h(NIcon, null, { default: () => h(icon) });
}

async function handleClick() {
  if (!auth.loggedIn) {
    auth.showLoginModal(undefined, { name: 'accountProfile' });
  } else if (!showUserDropdown.value) {
    showUserDropdown.value = true;
  }
}

function handleUserOptionSelect(key: string) {
  showUserDropdown.value = false;
  if (key === 'logout') {
    auth.logout();
  } else {
    const targetRoute = router.resolve({ name: key });
    if (targetRoute.meta.isTextSpecific) {
      router.push({ ...targetRoute, params: { ...targetRoute.params, text: state.text?.slug } });
    } else {
      router.push({ name: key });
    }
  }
}
</script>

<template>
  <n-dropdown
    :show="showUserDropdown"
    :options="userOptions"
    :on-clickoutside="() => (showUserDropdown = false)"
    :size="state.dropdownSize"
    show-arrow
    @select="handleUserOptionSelect"
  >
    <n-button
      :secondary="!auth.loggedIn"
      circle
      size="large"
      :title="tooltip"
      :focusable="false"
      :color="color"
      :style="auth.loggedIn && 'color: #fff'"
      class="user-options-button"
      @click="handleClick"
    >
      <template #icon>
        <n-icon v-if="auth.loggedIn" :component="PersonRound" />
        <n-icon v-else :component="LogInRound" />
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
