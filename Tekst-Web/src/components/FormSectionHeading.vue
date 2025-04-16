<script setup lang="ts">
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import { NFlex } from 'naive-ui';

defineProps<{
  label?: string;
  helpKey?: string;
}>();
</script>

<template>
  <n-flex v-if="label || $slots.default" align="center" :wrap="false" class="form-section-heading">
    <b class="text-medium text-color-accent">
      <slot>{{ label || '???' }}</slot>
    </b>
    <help-button-widget v-if="helpKey" :help-key="helpKey" />
  </n-flex>
</template>

<style scoped>
.form-section-heading {
  margin: var(--gap-md) 0;
  padding-bottom: 0.25rem;
  border-bottom: 1px solid var(--accent-color-fade3);
}

.form-section-heading:first-child {
  margin-top: 0.25rem;
}
</style>
