<script setup lang="ts">
import { type Component } from 'vue';
import { NIcon } from 'naive-ui';

withDefaults(
  defineProps<{
    level: '1' | '2' | '3' | '4' | '5' | '6';
    icon?: Component;
    iconSize?: string;
    iconColor?: 'text' | 'accent';
  }>(),
  {
    icon: undefined,
    iconSize: '1em',
    iconColor: 'text',
  }
);
</script>

<template>
  <component :is="`h${level}`" style="display: flex; align-items: center; gap: 0.5rem">
    <n-icon
      v-if="icon"
      :component="icon"
      :size="iconSize"
      :color="iconColor === 'accent' ? 'var(--accent-color)' : 'inherit'"
      style="opacity: 0.6"
    />
    <slot></slot>
  </component>
</template>
