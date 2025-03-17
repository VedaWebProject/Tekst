<script setup lang="ts">
import type { LocationMetadataResourceRead } from '@/api';
import { computed } from 'vue';

const props = withDefaults(
  defineProps<{
    resource: LocationMetadataResourceRead;
    focusView?: boolean;
  }>(),
  {
    focusView: false,
  }
);

const contents = computed(
  () =>
    props.resource.contents?.map((c) => ({
      id: c.id,
      entries: c.entries.map((e) => ({ key: e.key, value: e.value.join(', ') })),
    })) || []
);
</script>

<template>
  <div>
    <table :size="4" v-for="c in contents" :key="c.id">
      <tr v-for="entry in c.entries" :key="entry.key">
        <th class="b">{{ entry.key }}</th>
        <td>{{ entry.value }}</td>
      </tr>
    </table>
  </div>
</template>

<style scoped>
table th {
  text-align: left;
  padding-right: var(--gap-sm);
}
</style>
