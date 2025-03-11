<script setup lang="ts">
import { $t } from '@/i18n';
import { SortIcon } from '@/icons';
import { NBadge, NButton, NIcon, NPopselect } from 'naive-ui';
import { computed } from 'vue';

defineProps<{ disabled?: boolean }>();
const model = defineModel<string>();

const sortingPresetOptions = computed(() => [
  {
    type: 'group',
    label: $t('search.results.sortingPresets.title'),
    key: 'foo',
    children: [
      {
        label: () => $t('search.results.sortingPresets.relevance'),
        value: 'relevance',
      },
      {
        label: () => $t('search.results.sortingPresets.textLevelPosition'),
        value: 'text_level_position',
      },
      {
        label: () => $t('search.results.sortingPresets.textLevelRelevance'),
        value: 'text_level_relevance',
      },
    ],
  },
]);
const showDot = computed(() => !!model.value && model.value !== 'relevance');
</script>

<template>
  <n-popselect v-model:value="model" :options="sortingPresetOptions" :disabled="disabled">
    <n-badge :show="showDot" :offset="[-1, 4]" dot>
      <n-button :focusable="false" size="small" :disabled="disabled">
        <template #icon>
          <n-icon :component="SortIcon" />
        </template>
      </n-button>
    </n-badge>
  </n-popselect>
</template>
