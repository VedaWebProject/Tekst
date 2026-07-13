<script setup lang="ts">
import { NMenu } from 'naive-ui';
import type { MenuMixedOption } from 'naive-ui/es/menu/src/interface';

withDefaults(
  defineProps<{
    mode?: 'horizontal' | 'vertical';
    options?: MenuMixedOption[];
    secondary?: boolean;
  }>(),
  {
    mode: 'horizontal',
    options: undefined,
    secondary: false,
  }
);
const emit = defineEmits(['select']);
</script>

<template>
  <div class="mt-md mb-lg">
    <n-menu
      responsive
      :options="options"
      :dropdown-props="{
        showArrow: false,
        trigger: 'hover',
      }"
      :mode="mode"
      :class="{ secondary }"
      :value="$route.name?.toString()"
      @update:value="() => emit('select')"
    />
  </div>
</template>

<style scoped>
:deep(.n-menu.secondary > .v-overflow) {
  justify-content: center;
  align-items: center;
}

:deep(.n-menu.secondary) {
  font-size: var(--font-size-small);
  background-color: var(--main-bg-color);
  border-radius: var(--border-radius);
}

:deep(.n-menu:not(.secondary) .n-menu-item:first-of-type .n-menu-item-content) {
  padding-left: 0px;
}
</style>
