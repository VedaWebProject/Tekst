<script setup lang="ts">
import type { CSSProperties } from 'vue';
import { computed } from 'vue';

const props = withDefaults(
  defineProps<{
    wrap?: 'nowrap' | 'wrap' | 'wrap-reverse';
    groupWrap?: 'nowrap' | 'wrap' | 'wrap-reverse';
  }>(),
  {
    wrap: 'wrap',
    groupWrap: 'wrap',
  }
);

const containerStyle = computed<CSSProperties>(() => ({
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  flexWrap: props.wrap,
  gap: 'var(--gap-md)',
}));
</script>

<template>
  <div :style="containerStyle">
    <div class="sub-group" :style="{ flexWrap: groupWrap, justifyContent: 'flex-start' }">
      <slot name="start"></slot>
    </div>
    <div class="sub-group" :style="{ flexWrap: groupWrap, justifyContent: 'center' }">
      <slot name="center"></slot>
    </div>
    <div class="sub-group" :style="{ flexWrap: groupWrap, justifyContent: 'flex-end' }">
      <slot></slot>
    </div>
  </div>
</template>

<style scoped>
.sub-group {
  display: flex;
  align-items: center;
  gap: var(--gap-md);
}
</style>
