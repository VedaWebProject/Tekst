<script setup lang="ts">
import { RouterLink } from 'vue-router';
import type { UserReadPublic } from '@/api';
import UserDisplayText from '@/components/user/UserDisplayText.vue';
import UserAvatar from '@/components/user/UserAvatar.vue';

withDefaults(
  defineProps<{
    user?: UserReadPublic & Record<string, any>;
    showAvatar?: boolean;
    size?: 'large' | 'medium' | 'small' | 'tiny';
  }>(),
  {
    user: undefined,
    showAvatar: true,
    size: 'medium',
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
  <div
    style="display: flex; align-items: center; gap: 0.5rem"
    :style="size ? `font-size: var(--font-size-${size})` : ''"
  >
    <user-avatar
      v-if="showAvatar"
      :avatar-url="user?.avatarUrl || undefined"
      :size="iconSizes[size]"
    />
    <router-link v-if="user" :to="{ name: 'user', params: { username: user.username } }">
      <user-display-text :user="user" />
    </router-link>
    <span v-else>–</span>
  </div>
</template>
