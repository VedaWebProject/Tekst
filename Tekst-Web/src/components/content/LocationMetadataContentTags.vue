<script setup lang="ts">
import type { LocationMetadataContentRead, LocationMetadataResourceRead } from '@/api';
import ResourceInfoWidget from '@/components/resource/ResourceInfoWidget.vue';
import { useResourcesStore, useStateStore } from '@/stores';
import { groupAndSortItems, pickTranslation } from '@/utils';
import { NTag } from 'naive-ui';
import { computed } from 'vue';

const props = defineProps<{
  contents: LocationMetadataContentRead[];
}>();

const state = useStateStore();
const resources = useResourcesStore();

const tagColor = {
  color: 'var(--primary-color-fade5)',
  borderColor: 'var(--primary-color-fade4)',
  textColor: 'var(--primary-color)',
};

const contentsProcessed = computed(() => {
  const processed = [];
  for (const c of props.contents) {
    const res = resources.ofText.find((r) => r.id === c.resourceId) as LocationMetadataResourceRead;
    processed.push({
      id: c.id,
      res,
      resTitle: pickTranslation(res.title, state.locale),
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
        res: c.res,
        resTitle: c.resTitle,
        groups: c.groups.map((g) => {
          const groupLabel =
            pickTranslation(
              c.ei.groups.find((gg) => gg.key === g.group)?.translations,
              state.locale
            ) || g.group;
          return {
            group: groupLabel,
            items: g.items.map((i) => {
              const itemKey =
                pickTranslation(
                  c.ei.itemProps.find((props) => props.key === i.key)?.translations,
                  state.locale
                ) || null;
              const itemValue = i.value.join(', ');
              return {
                key: itemKey,
                value: itemValue,
                title: [c.resTitle, groupLabel, itemKey, itemValue].filter(Boolean).join(' > '),
              };
            }),
          };
        }),
        font: c.font,
      }))
  );
});
</script>

<template>
  <template v-for="content in contentsProcessed" :key="content.id">
    <template v-for="group in content.groups" :key="group.group">
      <resource-info-widget
        v-for="(item, index) in group.items"
        :key="`${item.key || 'no_key'}_${index}`"
        :resource="content.res"
      >
        <n-tag size="small" :color="tagColor" :title="item.title" class="loc-meta-tag">
          <span v-if="item.key">{{ item.key }}: </span>
          <span :style="{ 'font-family': content.font }">{{ item.value }}</span>
        </n-tag>
      </resource-info-widget>
    </template>
  </template>
</template>

<style scoped>
.loc-meta-tag {
  cursor: pointer;
}

.loc-meta-tag:hover {
  background-color: var(--primary-color-fade4);
}
</style>
