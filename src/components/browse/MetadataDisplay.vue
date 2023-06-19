<script setup lang="ts">
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';

const props = defineProps<{
  data?: Record<string, any>;
}>();

const { t, te } = useI18n({ useScope: 'global' });
const priority = ['author', 'year', 'language'];

const meta = computed<string[][] | null>(() => {
  const m: string[][] = [];
  const data = props.data || {};

  // prioritized keys first
  priority
    .filter((p: string) => p in data)
    .forEach((p: string) => {
      m.push([te(`models.meta.${p}`) ? t(`models.meta.${p}`) : p, data[p]]);
    });

  return m.length > 0 ? m : null;
});

const metaExtra = computed<string[][] | null>(() => {
  const m: string[][] = [];
  const data = props.data || {};

  Object.keys(data).forEach((p: string) => {
    if (!priority.includes(p)) {
      m.push([te(`models.meta.${p}`) ? t(`models.meta.${p}`) : p, data[p]]);
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
  font-size: var(--app-ui-font-size-medium);
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
