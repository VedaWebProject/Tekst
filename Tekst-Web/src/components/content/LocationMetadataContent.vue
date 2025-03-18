<script setup lang="ts">
import type { LocationMetadataContentRead, LocationMetadataResourceRead } from '@/api';
import { useStateStore } from '@/stores';
import { pickTranslation } from '@/utils';
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

const state = useStateStore();

const groups = props.resource.config.locationMetadata.groups.map((g, i) => ({
  name: g.name,
  index: i,
  label: pickTranslation(g.translations, state.locale),
}));
const displayProps = Object.fromEntries(
  props.resource.config.locationMetadata.displayProps.map((d, i) => [
    d.name,
    { index: i, label: pickTranslation(d.translations, state.locale), group: d.group },
  ])
);
const contents = computed(
  () => props.resource.contents?.map((c) => ({ id: c.id, groups: groupAndSort(c.entries) })) || []
);

function groupAndSort(entries: LocationMetadataContentRead['entries']): {
  groupName: string;
  groupLabel: string;
  entries: { key: string; value: string }[];
}[] {
  return groups.map((g) => ({
    groupName: g.name,
    groupLabel: g.label,
    entries: entries
      .filter((e) => displayProps[e.key].group === g.name)
      .sort(
        (a, b) =>
          (displayProps[a.key].index || Number.MAX_SAFE_INTEGER) -
          (displayProps[b.key].index || Number.MAX_SAFE_INTEGER)
      )
      .map((e) => ({ key: displayProps[e.key].label, value: e.value.join(', ') })),
  }));
}
</script>

<template>
  <div>
    <table :size="4" v-for="c in contents" :key="c.id">
      <template v-for="group in c.groups" :key="group.groupName">
        <tr>
          <td colspan="2" class="group-header text-color-accent text-small b">
            {{ group.groupLabel || group.groupName }}
          </td>
        </tr>
        <tr v-for="entry in group.entries" :key="entry.key">
          <th class="b">{{ entry.key }}</th>
          <td :style="{ fontFamily: resource.config.general.font || undefined }">
            {{ entry.value }}
          </td>
        </tr>
      </template>
    </table>
  </div>
</template>

<style scoped>
table {
  margin-top: -8px;
}
table th {
  text-align: left;
  padding-right: var(--gap-sm);
}
table .group-header {
  padding-top: 8px;
  border-bottom: 1px solid var(--accent-color-fade5);
}
</style>
