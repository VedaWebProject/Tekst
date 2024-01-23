<script setup lang="ts">
import { NButton, NIcon } from 'naive-ui';
import QuestionMarkOutlined from '@vicons/material/QuestionMarkOutlined';
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
      <n-icon :component="QuestionMarkOutlined" />
    </template>
  </n-button>
</template>

<style scoped></style>
