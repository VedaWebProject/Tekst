<script setup lang="ts">
import type { UserRead, UserReadPublic } from '@/api';
import { AdminIcon } from '@/icons';
import { NIcon } from 'naive-ui';

defineProps<{
  user?: UserRead | UserReadPublic;
}>();
</script>

<template>
  <div v-if="user" style="display: flex; flex-direction: column" class="n">
    <div style="display: flex; align-items: center; gap: 0.5rem">
      <span class="text-large">{{ user.name || `@${user.username}` }}</span>
      <span v-if="user.name" class="translucent text-small n"> @{{ user.username }} </span>
      <n-icon
        v-if="user.isSuperuser"
        :component="AdminIcon"
        color="var(--accent-color)"
        :title="$t('models.user.isSuperuser')"
      />
    </div>
    <span class="translucent text-small">{{ user.affiliation }}</span>
  </div>
</template>
