<script setup lang="ts">
import { NButton, NIcon } from 'naive-ui';
import HelpOutlineRound from '@vicons/material/HelpOutlineRound';
import { useI18n } from 'vue-i18n';

const { t } = useI18n({ useScope: 'global' });
</script>

<template>
  <n-button
    secondary
    circle
    @click="() => $router.push({ name: 'help' })"
    size="large"
    :title="t('nav.help')"
    :focusable="false"
  >
    <template #icon>
      <n-icon :component="HelpOutlineRound" />
    </template>
  </n-button>
</template>

<style scoped></style>
