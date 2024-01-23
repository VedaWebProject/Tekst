<script setup lang="ts">
import { type Component } from 'vue';
import { NEllipsis, NIcon } from 'naive-ui';

withDefaults(
  defineProps<{
    level: '1' | '2' | '3' | '4' | '5' | '6';
    icon?: Component;
    iconSize?: string;
    iconColor?: 'text' | 'accent';
    ellipsis?: boolean;
  }>(),
  {
    icon: undefined,
    iconSize: '1em',
    iconColor: 'accent',
  }
);
</script>

<template>
  <component :is="`h${level}`" style="display: flex; align-items: center; gap: var(--content-gap)">
    <n-icon
      v-if="icon"
      :component="icon"
      :size="iconSize"
      :color="iconColor === 'accent' ? 'var(--accent-color)' : 'inherit'"
    />
    <n-ellipsis v-if="ellipsis">
      <slot></slot>
    </n-ellipsis>
    <template v-else>
      <slot></slot>
    </template>
  </component>
</template>
