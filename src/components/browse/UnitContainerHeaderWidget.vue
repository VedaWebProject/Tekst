<script setup lang="ts">
import type { Component } from 'vue';
import { NButton, NIcon } from 'naive-ui';
const props = defineProps<{
  iconComponent: Component;
  title: string;
}>();
</script>

<template>
  <n-button quaternary circle :focusable="false" :title="props.title">
    <template #icon>
      <n-icon size="22px" :component="props.iconComponent" />
    </template>
  </n-button>
</template>
