<script setup lang="ts">
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import { NFlex } from 'naive-ui';

defineProps<{
  label?: string;
  helpKey?: string;
}>();
</script>

<template>
  <n-flex align="center" :wrap="false" class="form-section-heading">
    <b class="text-medium text-color-accent">{{ label }}</b>
    <help-button-widget v-if="helpKey" :help-key="helpKey" />
  </n-flex>
</template>

<style scoped>
.form-section-heading {
  margin: var(--gap-md) 0;
  border-bottom: 1px solid var(--accent-color-fade4);
}

.form-section-heading:first-child {
  margin-top: 0.25rem;
}
</style>
