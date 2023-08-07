<script setup lang="ts">
import { NButton, NIcon } from 'naive-ui';
import HelpOutlineRound from '@vicons/material/HelpOutlineRound';
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
      <n-icon :component="HelpOutlineRound" />
    </template>
  </n-button>
</template>

<style scoped></style>
