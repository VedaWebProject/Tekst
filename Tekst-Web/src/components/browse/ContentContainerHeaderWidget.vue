<script setup lang="ts">
import type { Component } from 'vue';
import { NButton, NIcon } from 'naive-ui';

const props = defineProps<{
  iconComponent: Component;
  title: string;
  disabled?: boolean;
  small?: boolean;
}>();
</script>

<template>
  <n-button
    quaternary
    circle
    :focusable="false"
    :title="title"
    :disabled="disabled"
    :size="small ? 'small' : undefined"
  >
    <template #icon>
      <n-icon size="22px" :component="props.iconComponent" />
    </template>
  </n-button>
</template>
