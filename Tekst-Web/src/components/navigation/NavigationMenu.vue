<script setup lang="ts">
import { useStateStore } from '@/stores';
import { NMenu } from 'naive-ui';
import type { MenuMixedOption } from 'naive-ui/es/menu/src/interface';
import { computed } from 'vue';

withDefaults(
  defineProps<{
    mode?: 'horizontal' | 'vertical';
    options?: MenuMixedOption[];
    embed?: boolean;
    center?: boolean;
  }>(),
  {
    mode: 'horizontal',
    options: undefined,
    embed: false,
    center: false,
  }
);
const emit = defineEmits(['select']);

const state = useStateStore();

const menuWrapperStyle = computed(() => ({
  display: 'flex',
  justifyContent: state.smallScreen ? 'flex-start' : 'center',
}));
</script>

<template>
  <div :style="menuWrapperStyle">
    <n-menu
      :options="options"
      :dropdown-props="{
        showArrow: false,
        trigger: 'hover',
      }"
      :mode="mode"
      :value="$route.name?.toString()"
      :class="{ embed, center }"
      @update:value="() => emit('select')"
    />
  </div>
</template>

<style scoped>
:deep(.n-menu) {
  width: 100%;
}

:deep(.n-menu.center) {
  justify-content: center;
}

:deep(.n-menu.embed) {
  background-color: var(--main-bg-color);
  border-radius: var(--border-radius);
  font-size: var(--font-size-medium);
}

:deep(.n-menu:not(.embed) > .n-menu-item:first-of-type .n-menu-item-content) {
  padding-left: 0px;
}

/* prevent menu item overflow as ellipsis */
:deep(.n-menu:not(.n-menu--responsive) .n-menu-item-content-header) {
  overflow: unset;
  text-overflow: unset;
}
</style>
