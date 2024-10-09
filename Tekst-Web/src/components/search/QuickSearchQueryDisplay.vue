<script setup lang="ts">
import type { QuickSearchRequestBody } from '@/api';
import { usePlatformData } from '@/composables/platformData';
import { computed } from 'vue';
import { NFlex, NTag, NIcon } from 'naive-ui';
import { useThemeStore } from '@/stores';
import { $t } from '@/i18n';
import { SearchIcon, SettingsIcon, TextsIcon } from '@/icons';

const props = withDefaults(
  defineProps<{
    req: QuickSearchRequestBody;
    total?: number;
    totalRelation?: 'eq' | 'gte';
    took?: number;
  }>(),
  {
    total: undefined,
    totalRelation: undefined,
    took: undefined,
  }
);

const { pfData } = usePlatformData();
const theme = useThemeStore();

const neutralTagColor = { color: 'var(--main-bg-color)' };

const targetTexts = computed(() => {
  return pfData.value?.texts.filter((t) => props.req.qck?.txt?.includes(t.id)) || [];
});
const settings = computed(() => [
  ...(props.req.qck?.op?.toLowerCase() === 'and'
    ? [$t('search.settings.quick.defaultOperator')]
    : []),
  ...(props.req.qck?.re ? [$t('search.settings.quick.regexp')] : []),
  ...(props.req.gen?.strict ? [$t('search.settings.general.strict')] : []),
]);
</script>

<template>
  <n-flex align="center" class="text-tiny" :size="[4, 8]">
    <span v-if="total != null && totalRelation">
      {{ totalRelation === 'eq' ? '' : '≥' }}
      {{
        $t('search.results.count', {
          count: total,
        })
      }}
    </span>
    <span v-else>
      {{ $t('search.results.searching') }}
    </span>

    <span>
      {{ $t('general.for') }}
    </span>

    <n-tag :color="neutralTagColor" :bordered="false" class="b content-font" size="small">
      <template #icon>
        <n-icon class="translucent" :component="SearchIcon" />
      </template>
      {{ req.q || '*' }}
    </n-tag>

    <span>
      {{ $t('general.in') }}
    </span>

    <n-tag
      v-for="text in targetTexts"
      :key="text.id"
      :color="{ color: theme.getAccentColors(text.id).fade4 }"
      :bordered="false"
      size="small"
    >
      <template #icon>
        <n-icon class="translucent" :component="TextsIcon" />
      </template>
      {{ text.title }}
    </n-tag>

    <span v-if="!!settings.length">{{ $t('general.with') }}</span>

    <template v-for="setting in settings" :key="setting">
      <n-tag :color="neutralTagColor" :bordered="false" size="small">
        <template #icon>
          <n-icon class="translucent" :component="SettingsIcon" />
        </template>
        {{ setting }}
      </n-tag>
    </template>

    <span v-if="took != null">
      {{
        $t('search.results.took', {
          ms: took,
        })
      }}
    </span>
    <span v-else>...</span>
  </n-flex>
</template>
