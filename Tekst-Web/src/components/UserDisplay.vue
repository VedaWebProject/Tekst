<script setup lang="ts">
import { NIcon } from 'naive-ui';
import { RouterLink } from 'vue-router';
import type { UserReadPublic } from '@/api';
import UserDisplayText from '@/components/UserDisplayText.vue';

import PersonFilled from '@vicons/material/PersonFilled';

withDefaults(
  defineProps<{
    user: UserReadPublic & Record<string, any>;
    showIcon?: boolean;
    size?: 'large' | 'medium' | 'small' | 'tiny' | 'mini';
  }>(),
  {
    showIcon: true,
    size: undefined,
  }
);
</script>

<template>
  <div
    v-if="user"
    style="display: flex; align-items: center"
    :style="size ? `font-size: var(--app-ui-font-size-${size})` : ''"
  >
    <n-icon v-if="showIcon" :component="PersonFilled" style="margin-right: 0.25rem" />
    <RouterLink :to="{ name: 'user', params: { username: user.username } }">
      <UserDisplayText :user="user" />
    </RouterLink>
  </div>
</template>
