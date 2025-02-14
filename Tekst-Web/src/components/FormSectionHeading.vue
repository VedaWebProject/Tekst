<script setup lang="ts">
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import { NDivider, NFlex } from 'naive-ui';

defineProps<{
  label?: string;
  helpKey?: string;
}>();
</script>

<template>
  <n-divider class="labeled-divider" title-placement="left">
    <n-flex align="center" :wrap="false">
      <span>{{ label }}</span>
      <help-button-widget v-if="helpKey" :help-key="helpKey" />
    </n-flex>
  </n-divider>
</template>

<style scoped>
.labeled-divider.n-divider:not(.n-divider--vertical) {
  margin: var(--gap-md) 0;
}

.labeled-divider.n-divider:not(.n-divider--vertical):first-child {
  margin-top: 0;
}

.labeled-divider.n-divider :deep(.n-divider__line.n-divider__line--left) {
  width: 14px;
}

.labeled-divider.n-divider:not(.n-divider--dashed) :deep(.n-divider__line) {
  background-color: var(--accent-color-fade4);
  height: 1px;
}

.labeled-divider.n-divider :deep(.n-divider__title) {
  color: var(--accent-color);
}
</style>
