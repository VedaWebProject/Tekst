<script setup lang="ts">
import { computed } from 'vue';
import { $t } from '@/i18n';
import { prioritizedMetadataKeys, type Metadata } from '@/api';

const props = defineProps<{
  data?: Metadata;
  resourceType?: string;
}>();

const meta = computed<string>(() => {
  const m: string[] = [];
  const data = props.data || [];

  prioritizedMetadataKeys.forEach((p: string) => {
    const v = data.find((d) => d.key === p)?.value;
    v && m.push(v);
  });

  props.resourceType && m.push($t(`resources.types.${props.resourceType}.label`));
  return m.join(', ');
});
</script>

<template>{{ meta }}</template>
