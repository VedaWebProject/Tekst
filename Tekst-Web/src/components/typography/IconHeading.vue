<script setup lang="ts">
import { type Component } from 'vue';
import { NIcon } from 'naive-ui';
import { useStateStore } from '@/stores';

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
    iconColor: 'accent',
  }
);

const state = useStateStore();
</script>

<template>
  <component :is="`h${level}`" style="display: flex; align-items: center; gap: var(--content-gap)">
    <n-icon
      v-if="icon && !state.smallScreen"
      :component="icon"
      :size="iconSize"
      :color="iconColor === 'accent' ? 'var(--accent-color)' : 'inherit'"
    />
    <slot></slot>
  </component>
</template>
