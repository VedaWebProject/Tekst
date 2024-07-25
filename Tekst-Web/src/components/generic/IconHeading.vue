<script setup lang="ts">
import { type CSSProperties, type Component } from 'vue';
import { NEllipsis, NIcon } from 'naive-ui';
import { useThemeStore } from '@/stores';

withDefaults(
  defineProps<{
    level: '1' | '2' | '3' | '4' | '5' | '6';
    icon?: Component;
    iconSize?: string;
    iconColor?: 'text' | 'accent';
    ellipsis?: boolean;
    style?: string | CSSProperties;
  }>(),
  {
    icon: undefined,
    iconSize: '1em',
    iconColor: 'accent',
    style: undefined,
  }
);

const theme = useThemeStore();
</script>

<template>
  <component
    :is="`h${level}`"
    style="display: flex; align-items: center; gap: var(--content-gap)"
    :style="style"
  >
    <n-icon
      v-if="icon"
      :component="icon"
      :size="iconSize"
      :color="iconColor === 'accent' ? theme.accentColors.base : 'inherit'"
    />
    <n-ellipsis v-if="ellipsis">
      <slot></slot>
    </n-ellipsis>
    <template v-else>
      <slot></slot>
    </template>
  </component>
</template>
