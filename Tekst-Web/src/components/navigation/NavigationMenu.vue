<script setup lang="ts">
import { NMenu } from 'naive-ui';
import type { MenuMixedOption } from 'naive-ui/es/menu/src/interface';

withDefaults(
  defineProps<{
    mode?: 'horizontal' | 'vertical';
    options?: MenuMixedOption[];
  }>(),
  {
    mode: 'horizontal',
    options: undefined,
  }
);
</script>

<template>
  <n-menu
    :options="options"
    :dropdown-props="{ size: 'medium', showArrow: true, trigger: 'click' }"
    :mode="mode"
    default-expand-all
    :value="$route.name?.toString()"
  />
</template>
