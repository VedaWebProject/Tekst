<script setup lang="ts">
import UserAvatar from '@/components/user/UserAvatar.vue';
import { $t } from '@/i18n';
import {
  AdminIcon,
  CommunityIcon,
  CorrectionNoteIcon,
  LoginIcon,
  LogoutIcon,
  MessageIcon,
  TextsIcon,
  UserIcon,
} from '@/icons';
import { useAuthStore, useResourcesStore, useStateStore, useUserMessagesStore } from '@/stores';
import { renderIcon } from '@/utils';
import { NBadge, NButton, NDropdown, NFlex, NIcon } from 'naive-ui';
import { computed, h, ref } from 'vue';
import { type RouteLocationRaw, RouterLink } from 'vue-router';

const auth = useAuthStore();
const userMessages = useUserMessagesStore();
const state = useStateStore();
const resources = useResourcesStore();

const tooltip = computed(() =>
  !!auth.user
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
    label: renderLink(() => $t('common.community'), {
      name: 'community',
    }),
    key: 'community',
    icon: renderIcon(CommunityIcon) || undefined,
  },
  ...(!!auth.user?.isSuperuser
    ? [
        {
          label: renderLink(() => $t('common.text', 2), {
            name: 'textSettings',
            params: {
              textSlug: state.text?.slug || '',
            },
          }),
          key: 'adminText',
          icon: renderIcon(TextsIcon),
        },
      ]
    : []),
  ...(!!auth.user?.isSuperuser
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
    label: $t('common.logout'),
    key: 'logout',
    icon: renderIcon(LogoutIcon),
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
    v-if="!!auth.user && !state.smallScreen"
    :options="userOptions"
    trigger="hover"
    placement="bottom-end"
    @select="handleUserOptionSelect"
  >
    <n-badge
      :show="!!userMessages.unreadCount || !!resources.correctionsCountTotal"
      :offset="[-8, 2]"
    >
      <template #value>
        <n-flex :wrap="false" size="small">
          <n-icon v-if="!!resources.correctionsCountTotal" :component="CorrectionNoteIcon" />
          <n-icon v-if="!!userMessages.unreadCount" :component="MessageIcon" />
        </n-flex>
      </template>
      <user-avatar
        :username="auth.user.username"
        :avatar-url="auth.user.avatarUrl"
        size="large"
        class="avatar-btn"
      />
    </n-badge>
  </n-dropdown>

  <n-button
    v-else
    type="primary"
    circle
    size="large"
    :title="tooltip"
    :focusable="false"
    @click="handleLoginClick"
  >
    <template #icon>
      <n-icon :component="LoginIcon" />
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
