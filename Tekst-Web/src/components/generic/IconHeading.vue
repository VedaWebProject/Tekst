<script setup lang="ts">
import { useThemeStore } from '@/stores';
import { NEllipsis, NIcon } from 'naive-ui';
import { type CSSProperties, type Component } from 'vue';

withDefaults(
  defineProps<{
    level: '1' | '2' | '3' | '4' | '5' | '6';
    icon?: Component;
    iconSize?: string;
    ellipsis?: boolean;
    style?: string | CSSProperties;
  }>(),
  {
    icon: undefined,
    iconSize: '1em',
    style: undefined,
  }
);

const theme = useThemeStore();
</script>

<template>
  <component :is="`h${level}`" class="icon-heading" :style="style">
    <n-icon v-if="icon" :component="icon" :size="iconSize" :color="theme.colors.primary.base" />
    <n-ellipsis v-if="ellipsis">
      <slot></slot>
    </n-ellipsis>
    <template v-else>
      <slot></slot>
    </template>
  </component>
</template>

<style scoped>
.icon-heading {
  display: flex;
  align-items: center;
  gap: var(--gap-md);
}
</style>
