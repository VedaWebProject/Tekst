<script setup lang="ts">
import { NButton, NIcon } from 'naive-ui';
import type { Component } from 'vue';

defineProps<{
  iconComponent: Component;
  title: string;
  full?: boolean;
  toggled?: boolean;
  highlight?: boolean;
}>();
</script>

<template>
  <n-button
    :quaternary="!toggled"
    :secondary="toggled"
    :type="toggled ? 'primary' : undefined"
    :block="full"
    :circle="!full"
    :color="highlight && !toggled ? 'var(--error-color)' : undefined"
    :focusable="false"
    :title="!full ? title : undefined"
    :style="{ 'justify-content': full ? 'flex-start' : undefined }"
  >
    <template #icon>
      <n-icon :component="iconComponent" />
    </template>
    <span v-if="full">
      {{ title }}
    </span>
  </n-button>
</template>
