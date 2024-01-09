<script setup lang="ts">
import type { CSSProperties } from 'vue';
import { computed } from 'vue';

const props = defineProps<{
  topGap?: boolean;
  bottomGap?: boolean;
  wrapReverse?: boolean;
}>();

const containerStyle = computed<CSSProperties>(() => ({
  display: 'flex',
  justifyContent: 'space-between',
  flexWrap: props.wrapReverse ? 'wrap-reverse' : 'wrap',
  gap: 'var(--content-gap)',
  marginTop: props.topGap ? 'var(--layout-gap)' : undefined,
  marginBottom: props.bottomGap ? 'var(--layout-gap)' : undefined,
}));
</script>

<template>
  <div :style="containerStyle">
    <div class="sub-group">
      <slot name="start"></slot>
    </div>
    <div class="sub-group">
      <slot name="center"></slot>
    </div>
    <div class="sub-group">
      <slot></slot>
    </div>
  </div>
</template>

<style scoped>
.sub-group {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: var(--content-gap);
}
</style>
