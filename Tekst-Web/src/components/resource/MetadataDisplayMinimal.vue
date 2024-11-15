<script setup lang="ts">
import { prioritizedMetadataKeys, type AnyResourceRead } from '@/api';
import { $t } from '@/i18n';
import { useStateStore } from '@/stores';
import { computed } from 'vue';

const props = defineProps<{
  resource: AnyResourceRead;
}>();

const state = useStateStore();

const meta = computed<string>(() => {
  const m: string[] = [];
  const data = props.resource.meta || [];

  // prioritized metadata goes first
  prioritizedMetadataKeys.forEach((p: string) => {
    const v = data.find((d) => d.key === p)?.value;
    if (v) m.push(v);
  });
  // resource type
  if (props.resource.resourceType)
    m.push($t(`resources.types.${props.resource.resourceType}.label`));
  // level
  const levelLabel = ` – ${$t('browse.location.level')}: ${state.textLevelLabels[props.resource.level]}`;
  // join metadata to string
  return m.join(', ') + levelLabel;
});
</script>

<template>{{ meta }}</template>
