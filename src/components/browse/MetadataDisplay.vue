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
      m.push([te(`meta.${p}`) ? t(`meta.${p}`) : p, data[p]]);
    });

  return m.length > 0 ? m : null;
});

const metaExtra = computed<string[][] | null>(() => {
  const m: string[][] = [];
  const data = props.data || {};

  Object.keys(data).forEach((p: string) => {
    if (!priority.includes(p)) {
      m.push([te(`meta.${p}`) ? t(`meta.${p}`) : p, data[p]]);
    }
  });

  return m.length > 0 ? m : null;
});
</script>

<template>
  <div class="metadata">
    <h3 v-if="meta" class="metadata-extra-subheading">
      {{ $t('meta.baseData') }}
    </h3>

    <template v-for="m in meta" :key="m[0]">
      <div class="metadata-category">{{ m[0] || '' }}</div>
      <div class="metadata-value">{{ m[1] || '' }}</div>
    </template>

    <h3 v-if="metaExtra" class="metadata-extra-subheading">
      {{ $t('meta.extraData') }}
    </h3>

    <template v-for="m in metaExtra" :key="m[0]">
      <div class="metadata-category">{{ m[0] || '' }}</div>
      <div class="metadata-value">{{ m[1] || '' }}</div>
    </template>
  </div>
</template>

<style scoped>
.metadata {
  display: grid;
  grid-template-columns: auto 1fr;

  font-size: var(--app-ui-font-size-medium);
}

.metadata > .metadata-category {
  font-weight: var(--app-ui-font-weight-normal);
  text-transform: capitalize;
}

.metadata > .metadata-value {
  font-weight: var(--app-ui-font-weight-light);
}

.metadata > .metadata-category,
.metadata > .metadata-value {
  background-color: rgba(0, 0, 0, 0.05);
  padding: 0.25rem 0.5rem;
}

.metadata > .metadata-extra-subheading {
  grid-column-start: 1;
  grid-column-end: 3;
}
</style>
