<script setup lang="ts">
import { computed } from 'vue';
import { $t, $te } from '@/i18n';
import type { Metadata, Metadate } from '@/api';

const props = defineProps<{
  data?: Metadata;
}>();

const priority = ['author', 'year', 'language'];

const meta = computed<string[][] | null>(() => {
  const m: string[][] = [];
  const data = props.data || [];

  // prioritized keys first
  priority.forEach((p: string) => {
    const v = data.find((d) => d.key === p)?.value;
    v && m.push([$te(`models.meta.${p}`) ? $t(`models.meta.${p}`) : p, v]);
  });

  return m.length > 0 ? m : null;
});

const metaExtra = computed<string[][] | null>(() => {
  const m: string[][] = [];
  const data = props.data || [];

  data.forEach((e: Metadate) => {
    if (!priority.includes(e.key)) {
      m.push([$te(`models.meta.${e.key}`) ? $t(`models.meta.${e.key}`) : e.key, e.value]);
    }
  });

  return m.length > 0 ? m : null;
});
</script>

<template>
  <div class="metadata">
    <template v-for="m in meta" :key="m[0]">
      <div class="metadata-category">{{ m[0] ? `${m[0]}:` : '' }}</div>
      <div class="metadata-value">{{ m[1] || '' }}</div>
    </template>
    <template v-for="m in metaExtra" :key="m[0]">
      <div class="metadata-category metadata-category-other">{{ m[0] ? `${m[0]}:` : '' }}</div>
      <div class="metadata-value">{{ m[1] || '' }}</div>
    </template>
  </div>
</template>

<style scoped>
.metadata {
  display: grid;
  grid-template-columns: auto 1fr;
  font-weight: var(--app-ui-font-weight-light);
}

.metadata > .metadata-category {
  text-transform: capitalize;
}

.metadata > .metadata-category {
  padding-right: 1rem;
}

.metadata > .metadata-category-other {
  font-style: italic;
}

.metadata > .metadata-extra-subheading {
  grid-column-start: 1;
  grid-column-end: 3;
}
</style>
