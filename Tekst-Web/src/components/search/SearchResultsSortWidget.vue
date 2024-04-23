<script setup lang="ts">
import { $t } from '@/i18n';
import { CheckCircleIcon, SortIcon } from '@/icons';
import { renderIcon } from '@/utils';
import { NDropdown, NButton, NIcon, NBadge, useThemeVars } from 'naive-ui';
import type { Size } from 'naive-ui/es/button/src/interface';
import { computed } from 'vue';

defineProps<{ size?: Size; disabled?: boolean }>();
const model = defineModel<string>();

const themeVars = useThemeVars();
const selectedIcon = renderIcon(CheckCircleIcon, themeVars.value.primaryColor);
const sortingPresetOptions = computed(() => [
  {
    label: () => $t('search.results.sortingPresets.relevance'),
    key: 'relevance',
    icon: !model.value || model.value === 'relevance' ? selectedIcon : undefined,
  },
  {
    label: () => $t('search.results.sortingPresets.textLevelPosition'),
    key: 'text_level_position',
    icon: model.value === 'text_level_position' ? selectedIcon : undefined,
  },
  {
    label: () => $t('search.results.sortingPresets.textLevelRelevance'),
    key: 'text_level_relevance',
    icon: model.value === 'text_level_relevance' ? selectedIcon : undefined,
  },
]);
const showDot = computed(() => !!model.value && model.value !== 'relevance');
</script>

<template>
  <n-dropdown
    trigger="click"
    :options="sortingPresetOptions"
    placement="bottom-end"
    @select="(v) => (model = v)"
  >
    <n-badge :show="showDot" :offset="[-1, 4]" dot>
      <n-button
        :focusable="false"
        :size="size"
        :disabled="disabled"
        :title="$t('search.results.sortingPresets.tooltip')"
      >
        <template #icon>
          <n-icon :component="SortIcon" />
        </template>
      </n-button>
    </n-badge>
  </n-dropdown>
</template>
