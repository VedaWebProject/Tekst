<script setup lang="ts">
import type { LocationMetadataResourceRead } from '@/api';
import { useStateStore } from '@/stores';
import { groupAndSortItems, pickTranslation } from '@/utils';
import { computed } from 'vue';
import CommonContentDisplay from './CommonContentDisplay.vue';

const props = withDefaults(
  defineProps<{
    resource: LocationMetadataResourceRead;
    focusView?: boolean;
    showComments?: boolean;
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
      authorsComment: c.authorsComment,
      editorsComment: c.editorsComment,
    })) || []
  )
    // pick translations for groups and item keys, join values
    .map((c) => ({
      ...c,
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

const fontStyle = {
  fontFamily: props.resource.config.general.font || 'var(--font-family-content)',
};
</script>

<template>
  <div>
    <common-content-display
      v-for="content in contents"
      :key="content.id"
      :show-comments="showComments"
      :authors-comment="content.authorsComment"
      :editors-comment="content.editorsComment"
      :font="fontStyle.fontFamily"
    >
      <table>
        <template v-for="(group, index) in content.groups" :key="group.group">
          <tr>
            <td colspan="2" class="group-header text-small b">
              <div :class="{ 'mt-sm': index > 0 }">
                {{ group.group || $t('common.other') }}
              </div>
            </td>
          </tr>
          <tr v-for="entry in group.items" :key="entry.key">
            <td style="padding-right: var(--gap-sm)">{{ entry.key }}</td>
            <td
              :style="{ fontFamily: resource.config.general.font || 'var(--font-family-content)' }"
            >
              {{ entry.value }}
            </td>
          </tr>
        </template>
      </table>
    </common-content-display>
  </div>
</template>

<style scoped>
table {
  border-collapse: collapse;
}

table th {
  text-align: left;
  padding-right: var(--gap-md);
}

table .group-header {
  border-bottom: 1px solid var(--primary-color-fade4);
}
</style>
