<script setup lang="ts">
import { QuestionMarkIcon } from '@/icons';
import { NButton, NIcon } from 'naive-ui';
</script>

<template>
  <n-button
    secondary
    circle
    size="large"
    :title="$t('nav.help')"
    :focusable="false"
    @click="() => $router.push({ name: 'help' })"
  >
    <template #icon>
      <n-icon :component="QuestionMarkIcon" />
    </template>
  </n-button>
</template>
