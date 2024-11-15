<script setup lang="ts">
import type { UserReadPublic } from '@/api';
import UserAvatar from '@/components/user/UserAvatar.vue';
import UserDisplayText from '@/components/user/UserDisplayText.vue';
import { AdminIcon } from '@/icons';
import { NFlex, NIcon } from 'naive-ui';
import { RouterLink } from 'vue-router';

withDefaults(
  defineProps<{
    user?: UserReadPublic & Record<string, unknown>;
    showAvatar?: boolean;
    size?: 'large' | 'medium' | 'small' | 'tiny';
    link?: boolean;
  }>(),
  {
    user: undefined,
    showAvatar: true,
    size: 'medium',
    link: true,
  }
);

const iconSizes = {
  large: 36,
  medium: 32,
  small: 28,
  tiny: 24,
};
</script>

<template>
  <n-flex align="center" :style="size ? `font-size: var(--font-size-${size})` : ''">
    <user-avatar
      v-if="showAvatar"
      :avatar-url="user?.avatarUrl || undefined"
      :size="iconSizes[size]"
      style="flex-shrink: 0"
    />
    <template v-if="user">
      <router-link v-if="link" :to="{ name: 'user', params: { username: user.username } }">
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
    <span v-else>–</span>
  </n-flex>
</template>
