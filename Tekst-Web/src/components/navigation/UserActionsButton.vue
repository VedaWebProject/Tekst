<script setup lang="ts">
import { ref, computed, h } from 'vue';
import { useAuthStore, useStateStore, useThemeStore } from '@/stores';
import { type RouteLocationRaw, RouterLink } from 'vue-router';
import { NBadge, NButton, NIcon, NDropdown } from 'naive-ui';
import { $t } from '@/i18n';
import { LogInIcon, LogOutIcon, UserIcon, AdminIcon, ResourceIcon } from '@/icons';
import { renderIcon } from '@/utils';
import { useUserMessages } from '@/composables/userMessages';

const auth = useAuthStore();
const { unreadCount: unreadUserMessagesCount } = useUserMessages();
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
    label: renderLink(
      () =>
        h('div', null, [
          auth.user?.name,
          h(
            NBadge,
            { dot: true, offset: [4, -10], show: !!unreadUserMessagesCount.value },
            undefined
          ),
        ]),
      {
        name: 'account',
      }
    ),
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

function renderLink(label: unknown, to: RouteLocationRaw, props?: Record<string, unknown>) {
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
    <n-badge :value="unreadUserMessagesCount">
      <n-button
        :secondary="!auth.loggedIn"
        circle
        size="large"
        :title="tooltip"
        :focusable="false"
        :color="theme.accentColors.base"
        class="user-options-button"
      >
        <template #icon>
          <n-icon :component="UserIcon" />
        </template>
      </n-button>
    </n-badge>
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
  font-size: var(--font-size-mini) !important;
}
</style>
