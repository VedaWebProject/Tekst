<script setup lang="ts">
import { LogoutIcon } from '@/icons';
import { NButton, NIcon } from 'naive-ui';

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
      <n-icon :component="LogoutIcon" />
    </template>
  </n-button>
</template>
