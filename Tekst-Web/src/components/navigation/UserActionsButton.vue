<script setup lang="ts">
import { ref, computed, h } from 'vue';
import { useAuthStore, useStateStore, useThemeStore, useUserMessagesStore } from '@/stores';
import { type RouteLocationRaw, RouterLink } from 'vue-router';
import { NBadge, NButton, NIcon, NDropdown } from 'naive-ui';
import { $t } from '@/i18n';
import { LogInIcon, LogOutIcon, UserIcon, AdminIcon, CommunityIcon, ResourceIcon } from '@/icons';
import { renderIcon } from '@/utils';
import UserAvatar from '@/components/user/UserAvatar.vue';

const auth = useAuthStore();
const userMessages = useUserMessagesStore();
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
          h(NBadge, { dot: true, offset: [4, -10], show: !!userMessages.unreadCount }, undefined),
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
  {
    label: renderLink(() => $t('community.heading'), {
      name: 'community',
    }),
    key: 'community',
    icon: renderIcon(CommunityIcon),
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
    v-if="auth.loggedIn && !state.smallScreen"
    :options="userOptions"
    :size="state.dropdownSize"
    to="#app-container"
    trigger="click"
    @select="handleUserOptionSelect"
  >
    <n-badge :value="userMessages.unreadCount">
      <user-avatar
        v-if="auth.user?.avatarUrl"
        :avatar-url="auth.user.avatarUrl"
        size="large"
        class="avatar-btn"
      />
      <n-button
        v-else
        circle
        size="large"
        :title="tooltip"
        :focusable="false"
        :color="theme.accentColors.base"
      >
        <template #icon>
          <n-icon :component="UserIcon" />
        </template>
      </n-button>
    </n-badge>
  </n-dropdown>

  <n-button
    v-else
    quaternary
    circle
    size="large"
    :title="tooltip"
    :focusable="false"
    @click="handleLoginClick"
  >
    <template #icon>
      <n-icon :component="LogInIcon" />
    </template>
  </n-button>
</template>

<style scoped>
.avatar-btn {
  cursor: pointer;
  transition: filter 0.2s ease-in-out;
}
.avatar-btn:hover {
  filter: brightness(1.1) saturate(1.1);
}
</style>
