<script setup lang="ts">
import type { Component } from 'vue';
import { NButton, NIcon } from 'naive-ui';

const props = defineProps<{
  iconComponent: Component;
  title: string;
  disabled?: boolean;
}>();
</script>

<template>
  <n-button quaternary circle :focusable="false" :title="props.title" :disabled="props.disabled">
    <template #icon>
      <n-icon size="22px" :component="props.iconComponent" />
    </template>
  </n-button>
</template>
