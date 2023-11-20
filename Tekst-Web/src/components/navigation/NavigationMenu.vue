<script setup lang="ts">
import { useStateStore } from '@/stores';
import { NMenu } from 'naive-ui';
import type { MenuMixedOption } from 'naive-ui/es/menu/src/interface';

withDefaults(
  defineProps<{
    mode?: 'horizontal' | 'vertical';
    options?: MenuMixedOption[];
    embed?: boolean;
  }>(),
  {
    mode: 'horizontal',
    options: undefined,
    embed: false,
  }
);

const state = useStateStore();
</script>

<template>
  <n-menu
    :options="options"
    :dropdown-props="{
      size: state.dropdownSize,
      showArrow: false,
      trigger: 'hover',
      to: '#app-container',
    }"
    :mode="mode"
    :value="$route.name?.toString()"
    :style="
      embed
        ? { backgroundColor: 'var(--main-bg-color)', borderRadius: 'var(--app-ui-border-radius)' }
        : undefined
    "
  />
</template>
