<script setup lang="ts">
import type { UserRead, UserReadPublic } from '@/api';
import { AdminIcon } from '@/icons';
import { NIcon, NFlex } from 'naive-ui';

defineProps<{
  user?: UserRead | UserReadPublic;
}>();
</script>

<template>
  <n-flex v-if="user" vertical size="small">
    <n-flex align="center" size="small">
      <span class="text-large">{{ user.name || `@${user.username}` }}</span>
      <n-flex align="center" size="small" :wrap="false">
        <span v-if="user.name" class="translucent text-small n"> @{{ user.username }} </span>
        <n-icon
          v-if="user.isSuperuser"
          :component="AdminIcon"
          color="var(--accent-color)"
          :title="$t('models.user.isSuperuser')"
        />
      </n-flex>
    </n-flex>
    <span class="translucent text-small">{{ user.affiliation }}</span>
  </n-flex>
</template>
