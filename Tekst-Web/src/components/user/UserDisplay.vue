<script setup lang="ts">
import type { UserReadPublic } from '@/api';
import UserAvatar from '@/components/user/UserAvatar.vue';
import UserDisplayText from '@/components/user/UserDisplayText.vue';
import { useLogo } from '@/composables/logo';
import { AdminIcon } from '@/icons';
import { useStateStore } from '@/stores';
import { NFlex, NIcon } from 'naive-ui';
import { RouterLink } from 'vue-router';

withDefaults(
  defineProps<{
    user?: UserReadPublic;
    showAvatar?: boolean;
    size?: 'large' | 'medium' | 'small';
    link?: boolean;
    system?: boolean;
  }>(),
  {
    user: undefined,
    showAvatar: true,
    size: 'medium',
    link: true,
  }
);

const iconSizes = {
  large: 34,
  medium: 30,
  small: 22,
};

const state = useStateStore();
const { pageLogo } = useLogo();
</script>

<template>
  <n-flex align="center" :size="size" :style="`font-size: var(--font-size-${size})`">
    <user-avatar
      v-if="showAvatar"
      :avatar-url="!system ? user.avatarUrl || undefined : pageLogo"
      :size="iconSizes[size]"
      style="flex-shrink: 0"
    />
    <template v-if="user">
      <span v-if="system">{{ state.pf?.state.platformName }}:</span>
      <router-link
        v-if="link"
        :to="{ name: 'user', params: { username: user.username } }"
        @click.stop.prevent
      >
        <user-display-text :user="user" />
      </router-link>
      <user-display-text v-else :user="user" />
      <n-icon
        v-if="user.isSuperuser"
        :component="AdminIcon"
        color="var(--accent-color)"
        :title="$t('models.user.isSuperuser')"
      />
    </template>
    <span v-else-if="system"> {{ state.pf?.state.platformName }} </span>
    <span v-else>–</span>
  </n-flex>
</template>
