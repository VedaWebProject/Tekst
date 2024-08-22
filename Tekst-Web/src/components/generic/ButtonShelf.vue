<script setup lang="ts">
import type { CSSProperties } from 'vue';
import { computed } from 'vue';

const props = withDefaults(
  defineProps<{
    topGap?: boolean;
    bottomGap?: boolean;
    wrap?: 'nowrap' | 'wrap' | 'wrap-reverse';
    groupWrap?: 'nowrap' | 'wrap' | 'wrap-reverse';
  }>(),
  {
    topGap: false,
    bottomGap: false,
    wrap: 'wrap',
    groupWrap: 'wrap',
  }
);

const containerStyle = computed<CSSProperties>(() => ({
  display: 'flex',
  justifyContent: 'space-between',
  flexWrap: props.wrap,
  gap: 'var(--gap-md)',
  marginTop: props.topGap ? 'var(--gap-lg)' : undefined,
  marginBottom: props.bottomGap ? 'var(--gap-lg)' : undefined,
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
  gap: var(--gap-md);
}
</style>
