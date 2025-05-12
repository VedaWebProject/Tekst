<script setup lang="ts">
import type { LocationMetadataContentRead, LocationMetadataResourceRead } from '@/api';
import { useResourcesStore, useStateStore } from '@/stores';
import { groupAndSortItems, pickTranslation } from '@/utils';
import { NCollapse, NCollapseItem, NFlex } from 'naive-ui';
import { computed } from 'vue';

const props = defineProps<{
  contents: LocationMetadataContentRead[];
}>();

const expand = defineModel<boolean>('expand');

const state = useStateStore();
const resources = useResourcesStore();

// const contentsProcessed = computed(() => props.contents.map((c) => ({
//   content: c,
//   cfg: (resources.ofText.find((r) => r.id === c.resourceId) as LocationMetadataResourceRead)?.config,
// })));

const contentsProcessed = computed(() => {
  const processed = [];
  for (const c of props.contents) {
    const res = resources.ofText.find((r) => r.id === c.resourceId) as LocationMetadataResourceRead;
    processed.push({
      id: c.id,
      ei: res.config.special.entriesIntegration,
      font: res.config.general.font || 'var(--font-family-content)',
      groups: groupAndSortItems(c.entries, res.config.special.entriesIntegration),
      authorsComment: c.authorsComment,
      editorsComment: c.editorsComment,
    });
  }
  // transform contents, group and sort entries
  return (
    processed
      // pick translations for groups and item keys, join values
      .map((c) => ({
        ...c,
        id: c.id,
        groups: c.groups.map((g) => ({
          group:
            pickTranslation(
              c.ei.groups.find((gg) => gg.key === g.group)?.translations,
              state.locale
            ) || g.group,
          items: g.items.map((i) => ({
            key:
              pickTranslation(
                c.ei.itemProps.find((props) => props.key === i.key)?.translations,
                state.locale
              ) || i.key,
            value: i.value.join(', '),
          })),
        })),
        font: c.font,
      }))
  );
});
</script>

<template>
  <div class="gray-box" style="padding: var(--gap-md)">
    <n-collapse
      :default-expanded-names="expand ? ['meta'] : []"
      @update:expanded-names="(exp: string[]) => (expand = exp.includes('meta'))"
    >
      <n-collapse-item
        :title="$t('resources.types.locationMetadata.label')"
        name="meta"
        class="text-mini m-0"
      >
        <n-flex align="stretch" :size="[32, 16]" class="text-small">
          <template v-for="content in contentsProcessed" :key="content.id">
            <div v-for="group in content.groups" :key="group.group" class="table-container">
              <table>
                <tbody>
                  <tr>
                    <td colspan="2" class="b text-tiny text-color-accent">
                      {{ group.group || $t('common.other') }}
                    </td>
                  </tr>
                  <tr v-for="entry in group.items" :key="entry.key">
                    <td style="padding-right: var(--gap-sm)">{{ entry.key }}</td>
                    <td :style="{ fontFamily: content.font }">
                      {{ entry.value }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </template>
        </n-flex>
      </n-collapse-item>
    </n-collapse>
  </div>
</template>

<style scoped>
.n-collapse
  > .n-collapse-item
  > :deep(.n-collapse-item__content-wrapper .n-collapse-item__content-inner) {
  padding-top: var(--gap-sm);
}

.n-collapse > .n-collapse-item > :deep(.n-collapse-item__header .n-collapse-item__header-main) {
  font-size: var(--font-size-small);
}

.table-container {
  border-left: 1px solid var(--accent-color-fade3);
}

table {
  border-collapse: collapse;
}

table td {
  padding-left: var(--gap-sm);
}

table th {
  text-align: left;
  padding-right: var(--gap-md);
}
</style>
