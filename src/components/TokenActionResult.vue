<script setup lang="ts">
import { NIcon, NSpin } from 'naive-ui';

import KeyOffTwotone from '@vicons/material/KeyOffTwotone';
import CheckCircleTwotone from '@vicons/material/CheckCircleTwotone';

const props = defineProps<{
  message: string;
  success: boolean;
  loading: boolean;
}>();
</script>

<template>
  <div v-if="props.loading" style="padding: 2rem; text-align: center">
    <n-spin>
      <template #description>
        {{ $t('init.loading') }}
      </template>
    </n-spin>
  </div>

  <div v-else class="token-action-result">
    <n-icon size="128" :component="props.success ? CheckCircleTwotone : KeyOffTwotone" />
    <div style="font-size: var(--app-ui-font-size-huge)">{{ props.message }}</div>
  </div>
</template>

<style scoped>
.token-action-result {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 2rem 0 3rem 0;
  opacity: 0.75;
}

.token-action-result > * {
  text-align: center;
}
</style>
