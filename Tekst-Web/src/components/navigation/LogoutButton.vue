<script setup lang="ts">
import { NButton, NIcon } from 'naive-ui';
import { LogOutIcon } from '@/icons';

const emit = defineEmits(['click']);
</script>

<template>
  <n-button
    secondary
    type="primary"
    circle
    size="large"
    :title="$t('account.logoutBtn')"
    :focusable="false"
    @click="
      () => {
        emit('click');
        $router.push({ name: 'logout' });
      }
    "
  >
    <template #icon>
      <n-icon :component="LogOutIcon" />
    </template>
  </n-button>
</template>
