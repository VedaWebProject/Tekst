<script setup lang="ts">
import { $t } from '@/i18n';
import { SortIcon } from '@/icons';
import { NPopselect, NButton, NIcon, NBadge } from 'naive-ui';
import type { Size } from 'naive-ui/es/button/src/interface';
import { computed } from 'vue';

defineProps<{ size?: Size; disabled?: boolean }>();
const model = defineModel<string>();

const sortingPresetOptions = computed(() => [
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
]);
const showDot = computed(() => !!model.value && model.value !== 'relevance');
</script>

<template>
  <n-popselect
    v-model:value="model"
    :options="sortingPresetOptions"
  >
    <n-badge :show="showDot" :offset="[-1, 4]" dot>
      <n-button secondary :focusable="false" :size="size" :disabled="disabled">
        <template #icon>
          <n-icon :component="SortIcon" />
        </template>
        {{ $t('search.results.sortingPresets.title') }}
      </n-button>
    </n-badge>
  </n-popselect>
</template>
