<script setup lang="ts">
import { NScrollbar, NCollapse, NCollapseItem } from 'naive-ui';
</script>

<template>
  <slot></slot>
  <n-collapse v-if="$slots.details" class="mt-md">
    <n-collapse-item :title="$t('general.details')" name="details" class="text-mini m-0">
      <n-scrollbar class="details-scroll-container">
        <pre class="details">
          <slot name="details"></slot>
        </pre>
      </n-scrollbar>
    </n-collapse-item>
  </n-collapse>
</template>

<style scoped>
.details {
  font-family: monospace;
  font-size: var(--font-size-mini);
  white-space: pre-wrap;
  line-height: 1;
}

:deep(.n-scrollbar.details-scroll-container) {
  max-height: 120px;
  background-color: #00000010;
  border-radius: 3px;
  padding: 0.5rem;
}
</style>
