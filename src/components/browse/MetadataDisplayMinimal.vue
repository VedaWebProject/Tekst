<script setup lang="ts">
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';

const props = defineProps<{
  data?: Record<string, any>;
  layerType?: string;
}>();

const { t } = useI18n({ useScope: 'global' });

const meta = computed<string>(() => {
  const minimalMeta = ['author', 'year', 'language'];
  const m: string[] = [];
  const data = props.data || {};

  minimalMeta.forEach((p: string) => {
    if (p in data) {
      m.push(data[p]);
    }
  });

  props.layerType && m.push(t(`layerTypes.${props.layerType}`));
  return m.join(', ');
});
</script>

<template>{{ meta }}</template>
