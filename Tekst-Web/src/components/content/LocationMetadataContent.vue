<script setup lang="ts">
import type { LocationMetadataResourceRead } from '@/api';
import { useStateStore } from '@/stores';
import { groupAndSortItems, pickTranslation } from '@/utils';
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

const contents = computed(() =>
  // transform contents, group and sort entries
  (
    props.resource.contents?.map((c) => ({
      id: c.id,
      groups: groupAndSortItems(c.entries, props.resource.config.special.entriesIntegration),
    })) || []
  )
    // pick translations for groups and item keys, join values
    .map((c) => ({
      id: c.id,
      groups: c.groups.map((g) => ({
        group:
          pickTranslation(
            props.resource.config.special.entriesIntegration.groups.find((gg) => gg.key === g.group)
              ?.translations,
            state.locale
          ) || g.group,
        items: g.items.map((i) => ({
          key:
            pickTranslation(
              props.resource.config.special.entriesIntegration.itemProps.find(
                (props) => props.key === i.key
              )?.translations,
              state.locale
            ) || i.key,
          value: i.value.join(', '),
        })),
      })),
    }))
);
</script>

<template>
  <div>
    <table :size="4" v-for="c in contents" :key="c.id">
      <template v-for="group in c.groups" :key="group.group">
        <tr>
          <td colspan="2" class="group-header text-small b">
            {{ group.group || $t('common.other') }}
          </td>
        </tr>
        <tr v-for="entry in group.items" :key="entry.key">
          <td style="padding-right: var(--gap-sm)">{{ entry.key }}:</td>
          <td :style="{ fontFamily: resource.config.general.font || 'var(--font-family-content)' }">
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
