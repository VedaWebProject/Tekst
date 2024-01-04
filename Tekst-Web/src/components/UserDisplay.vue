<script setup lang="ts">
import { NIcon } from 'naive-ui';
import { RouterLink } from 'vue-router';
import type { UserReadPublic } from '@/api';
import UserDisplayText from '@/components/UserDisplayText.vue';

import PersonFilled from '@vicons/material/PersonFilled';

withDefaults(
  defineProps<{
    user?: UserReadPublic & Record<string, any>;
    showIcon?: boolean;
    size?: 'large' | 'medium' | 'small' | 'tiny' | 'mini';
  }>(),
  {
    user: undefined,
    showIcon: true,
    size: undefined,
  }
);
</script>

<template>
  <div
    style="display: flex; align-items: center"
    :style="size ? `font-size: var(--app-ui-font-size-${size})` : ''"
  >
    <n-icon v-if="showIcon" :component="PersonFilled" style="margin-right: 0.25rem" />
    <RouterLink v-if="user" :to="{ name: 'user', params: { username: user.username } }">
      <UserDisplayText :user="user" />
    </RouterLink>
    <span v-else>–</span>
  </div>
</template>
