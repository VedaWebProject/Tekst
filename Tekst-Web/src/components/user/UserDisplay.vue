<script setup lang="ts">
import type { UserReadPublic } from '@/api';
import UserAvatar from '@/components/user/UserAvatar.vue';
import UserDisplay from '@/components/user/UserDisplay.vue';
import { useLogo } from '@/composables/logo';
import { AdminIcon } from '@/icons';
import { useStateStore } from '@/stores';
import { userDisplayText } from '@/utils';
import { NButton, NDropdown, NFlex, NIcon, type DropdownOption } from 'naive-ui';
import { computed, h, type VNodeChild } from 'vue';
import { useRouter } from 'vue-router';

const iconSizes = {
  large: 34,
  medium: 30,
  small: 22,
};

const props = withDefaults(
  defineProps<{
    user?: UserReadPublic | UserReadPublic[];
    size?: 'large' | 'medium' | 'small';
    link?: boolean;
    system?: boolean;
  }>(),
  {
    user: undefined,
    size: 'medium',
    link: true,
  }
);

const state = useStateStore();
const router = useRouter();
const { pageLogo } = useLogo();

const users = computed(() =>
  props.user ? (Array.isArray(props.user) ? props.user : [props.user]) : []
);
const options = computed(() =>
  users.value.map((u) => ({
    key: u.id,
    label: userDisplayText(u),
    user: u,
  }))
);

function renderOptionLabel(option: DropdownOption): VNodeChild {
  return h(UserDisplay, { user: option.user as UserReadPublic, link: false, size: 'small' });
}

function handleUserClick(user: UserReadPublic) {
  router.push({ name: 'user', params: { username: user.username } });
}
</script>

<template>
  <n-flex
    align="center"
    :size="size"
    :wrap="false"
    :title="$t('resources.ownerTip')"
    v-bind="$attrs"
  >
    <template v-if="system">
      <user-avatar
        username="system"
        :avatar-url="pageLogo"
        :size="iconSizes[size]"
        style="flex-shrink: 0"
      />
      <span>{{ state.pf?.state.platformName ?? '–' }}</span>
    </template>
    <template v-else-if="users.length == 1">
      <user-avatar
        :username="users[0].username"
        :avatar-url="users[0].avatarUrl"
        :size="iconSizes[size]"
        style="flex-shrink: 0"
      />
      <n-button
        v-if="link"
        text
        :focusable="false"
        @click.stop.prevent="() => handleUserClick(users[0])"
        :size="size"
      >
        {{ userDisplayText(users[0]) }}
      </n-button>
      <span v-else>{{ userDisplayText(users[0]) }}</span>
      <n-icon
        v-if="users[0].isSuperuser"
        :component="AdminIcon"
        color="var(--primary-color)"
        :title="$t('models.user.isSuperuser')"
      />
    </template>
    <template v-else-if="users.length > 1">
      <n-dropdown
        :options="options"
        :render-label="renderOptionLabel"
        @select="(_, o) => handleUserClick(o.user as UserReadPublic)"
      >
        <n-button text :focusable="false" :size="size">
          <n-flex align="center" size="small">
            <div :style="{ marginRight: `-${8 * (users.length - 1)}px` }">
              <user-avatar
                v-for="(user, index) in users"
                :key="user.id"
                :username="user.username"
                :avatar-url="user.avatarUrl"
                :size="iconSizes[size]"
                :style="{
                  position: 'relative',
                  left: `-${8 * index}px`,
                  outline: '2px solid var(--content-bg-color)',
                }"
              />
            </div>
            <span>
              {{ userDisplayText(users[0], false) }}
              <b>+{{ users.length - 1 }}</b>
            </span>
          </n-flex>
        </n-button>
      </n-dropdown>
    </template>
  </n-flex>
</template>
