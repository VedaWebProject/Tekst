<script setup lang="ts">
import { NButton, NIcon } from 'naive-ui';
import { QuestionMarkIcon } from '@/icons';
</script>

<template>
  <n-button
    quaternary
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
