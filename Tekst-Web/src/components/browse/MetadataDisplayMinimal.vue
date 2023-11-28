<script setup lang="ts">
import { computed } from 'vue';
import { $t } from '@/i18n';
import type { Metadata } from '@/api';

const props = defineProps<{
  data?: Metadata;
  layerType?: string;
}>();

const meta = computed<string>(() => {
  const minimalMeta = ['author', 'year', 'language'];
  const m: string[] = [];
  const data = props.data || [];

  minimalMeta.forEach((p: string) => {
    const v = data.find((d) => d.key === p)?.value;
    v && m.push(v);
  });

  props.layerType && m.push($t(`layerTypes.${props.layerType}`));
  return m.join(', ');
});
</script>

<template>{{ meta }}</template>
