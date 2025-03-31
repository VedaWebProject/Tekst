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

const groups = props.resource.config.special.itemDisplay.groups.map((g, i) => ({
  name: g.name,
  index: i,
  label: pickTranslation(g.translations, state.locale),
}));
const displayProps = Object.fromEntries(
  props.resource.config.special.itemDisplay.displayProps.map((d, i) => [
    d.name,
    { index: i, label: pickTranslation(d.translations, state.locale), group: d.group },
  ])
);
const contents = computed(
  () => props.resource.contents?.map((c) => ({ id: c.id, groups: groupAndSort(c.entries) })) || []
);

function compareEntries(
  a: LocationMetadataContentRead['entries'][number],
  b: LocationMetadataContentRead['entries'][number]
): number {
  const comp =
    (displayProps[a.key] ? displayProps[a.key].index : Number.MAX_SAFE_INTEGER) -
    (displayProps[b.key] ? displayProps[b.key].index : Number.MAX_SAFE_INTEGER);
  if (comp !== 0) return comp;
  return a.key.localeCompare(b.key);
}

function groupAndSort(entries: LocationMetadataContentRead['entries']): {
  name?: string;
  label?: string;
  entries: { key: string; value: string }[];
}[] {
  const grouped = groups.map((g) => ({
    name: g.name,
    label: g.label,
    entries: entries
      .filter((e) => !!displayProps[e.key] && displayProps[e.key].group === g.name)
      .sort(compareEntries)
      .map((e) => ({
        key: displayProps[e.key]?.label || e.key,
        value: e.value.join(', '),
      })),
  }));
  const ungrouped = [
    {
      name: undefined,
      label: undefined,
      entries: entries
        .filter(
          (e) =>
            !displayProps[e.key] ||
            !displayProps[e.key].group ||
            !groups.map((g) => g.name).includes(displayProps[e.key].group as string)
        )
        .sort(compareEntries)
        .map((e) => ({
          key: displayProps[e.key]?.label || e.key,
          value: e.value.join(', '),
        })),
    },
  ];
  return [...grouped, ...ungrouped];
}
</script>

<template>
  <div>
    <table :size="4" v-for="c in contents" :key="c.id">
      <template v-for="group in c.groups" :key="group.name">
        <tr>
          <td colspan="2" class="group-header text-small b">
            {{ group.label || group.name || $t('common.other') }}
          </td>
        </tr>
        <tr v-for="entry in group.entries" :key="entry.key">
          <td style="padding-right: var(--gap-sm)">{{ entry.key }}:</td>
          <td :style="{ fontFamily: resource.config.general.font || 'Tekst Content Font' }">
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
