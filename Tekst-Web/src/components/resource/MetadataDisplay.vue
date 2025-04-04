<script setup lang="ts">
import { prioritizedMetadataKeys, type Metadata, type MetadataEntry } from '@/api';
import { $t, $te } from '@/i18n';
import { computed } from 'vue';

const props = defineProps<{
  data?: Metadata;
  contentFont?: string;
}>();

const meta = computed<string[][] | null>(() => {
  const m: string[][] = [];
  const data = props.data || [];

  // prioritized keys first
  prioritizedMetadataKeys.forEach((p: string) => {
    const v = data.find((d) => d.key === p)?.value;
    if (v) m.push([$te(`models.meta.${p}`) ? $t(`models.meta.${p}`) : p, v]);
  });

  return m.length > 0 ? m : null;
});

const metaExtra = computed<string[][] | null>(() => {
  const m: string[][] = [];
  const data = props.data || [];

  data.forEach((e: MetadataEntry) => {
    if (!prioritizedMetadataKeys.includes(e.key)) {
      m.push([$te(`models.meta.${e.key}`) ? $t(`models.meta.${e.key}`) : e.key, e.value]);
    }
  });

  return m.length > 0 ? m : null;
});
</script>

<template>
  <table>
    <tr v-for="m in meta" :key="m[0]">
      <td class="metadata-category">{{ m[0] ? `${m[0]}:` : '' }}</td>
      <td :style="{ fontFamily: contentFont }">{{ m[1] || '' }}</td>
    </tr>
    <tr v-for="m in metaExtra" :key="m[0]">
      <td class="metadata-category i">{{ m[0] ? `${m[0]}:` : '' }}</td>
      <td :style="{ fontFamily: contentFont }">{{ m[1] || '' }}</td>
    </tr>
  </table>
</template>

<style scoped>
table td {
  vertical-align: top;
}

table td.metadata-category {
  white-space: nowrap;
  text-transform: capitalize;
  padding-right: var(--gap-sm);
}
</style>
