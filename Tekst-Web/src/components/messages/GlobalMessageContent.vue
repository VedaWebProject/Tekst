<script setup lang="ts">
import { NCollapse, NCollapseItem, NScrollbar } from 'naive-ui';
</script>

<template>
  <slot></slot>
  <n-collapse v-if="$slots.details" class="mt-md">
    <n-collapse-item :title="$t('general.details')" name="details" class="text-mini m-0">
      <n-scrollbar class="details-scroll-container">
        <pre class="details pre-wrap text-mini">
          <slot name="details"></slot>
        </pre>
      </n-scrollbar>
    </n-collapse-item>
  </n-collapse>
</template>

<style scoped>
.details {
  font-family: monospace;
  line-height: 1;
}

:deep(.n-scrollbar.details-scroll-container) {
  max-height: 120px;
  background-color: #00000010;
  border-radius: 3px;
  padding: 0.5rem;
}
</style>
