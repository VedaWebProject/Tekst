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
  }>(),
  {
    showIcon: true,
  }
);
</script>

<template>
  <div v-if="user" style="display: flex; align-items: center">
    <n-icon v-if="showIcon" :component="PersonFilled" style="margin-right: 4px" />
    <RouterLink :to="{ name: 'user', params: { username: user.username } }">
      <UserDisplayText :user="user" />
    </RouterLink>
  </div>
</template>
