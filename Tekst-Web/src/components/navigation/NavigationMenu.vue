<script setup lang="ts">
import { useStateStore } from '@/stores';
import { NMenu } from 'naive-ui';
import type { MenuMixedOption } from 'naive-ui/es/menu/src/interface';
import { computed } from 'vue';

const props = withDefaults(
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

const state = useStateStore();

const menuWrapperStyle = computed(() => ({
  display: 'flex',
  justifyContent: state.smallScreen ? 'flex-start' : 'center',
}));

const menuStyle = computed(() => ({
  backgroundColor: props.embed ? 'var(--main-bg-color)' : 'transparent',
  borderRadius: props.embed ? 'var(--app-ui-border-radius)' : undefined,
  justifyContent: props.center ? 'center' : undefined,
  width: state.smallScreen ? '100%' : 'auto',
}));
</script>

<template>
  <div :style="menuWrapperStyle">
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
      :style="menuStyle"
    />
  </div>
</template>
