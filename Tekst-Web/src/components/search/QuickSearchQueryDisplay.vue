<script setup lang="ts">
import type { QuickSearchRequestBody } from '@/api';
import { $t } from '@/i18n';
import { SearchIcon, SettingsIcon, TextsIcon } from '@/icons';
import { useStateStore, useThemeStore } from '@/stores';
import { NFlex, NIcon, NTag } from 'naive-ui';
import { computed } from 'vue';

const props = withDefaults(
  defineProps<{
    req: QuickSearchRequestBody;
    total?: number;
    totalRelation?: 'eq' | 'gte';
    loading?: boolean;
  }>(),
  {
    total: undefined,
    totalRelation: undefined,
  }
);

const state = useStateStore();
const theme = useThemeStore();

const targetTexts = computed(() => {
  return state.pf?.texts
    .filter((t) => !props.req.qck.txt?.length || props.req.qck.txt.includes(t.id))
    ?.map((t) => ({
      ...t,
      color: theme.getTextColors(t.id).base,
      colorFade: theme.getTextColors(t.id).fade3,
    }));
});
const settings = computed(() => [
  ...(props.req.qck?.op?.toLowerCase() === 'and'
    ? [$t('search.settings.quick.defaultOperator')]
    : []),
  ...(props.req.qck?.re ? [$t('search.settings.quick.regexp')] : []),
  ...(props.req.qck?.inh ? [$t('search.settings.quick.inheritedContents')] : []),
  ...(props.req.qck?.allLvls ? [$t('search.settings.quick.allLevels')] : []),
  ...(props.req.gen?.strict ? [$t('search.settings.general.strict')] : []),
]);
</script>

<template>
  <n-flex align="center" class="text-tiny" :size="[4, 8]">
    <span v-if="!loading && total != null && totalRelation">
      {{ $t('search.quickSearch.title') }}:
      {{ totalRelation === 'eq' ? '' : '≥' }}
      <b>{{ $t('search.results.count', { count: total }) }}</b>
      {{ $t('common.for') }}
    </span>
    <span v-else>
      {{ $t('search.results.searching') }}
    </span>

    <n-tag class="b font-content" size="small">
      <template #icon>
        <n-icon class="translucent" :component="SearchIcon" />
      </template>
      {{ req.q || '*' }}
    </n-tag>

    <span>
      {{ $t('common.in') }}
    </span>

    <template v-if="!!targetTexts?.length">
      <n-tag
        v-for="text in targetTexts"
        :key="text.id"
        :color="{ borderColor: text.colorFade, textColor: text.color }"
        size="small"
      >
        <template #icon>
          <n-icon class="translucent" :component="TextsIcon" />
        </template>
        {{ text.title }}
      </n-tag>
    </template>
    <b v-else>{{ $t('search.results.allTexts') }}</b>

    <span v-if="!!settings.length">{{ $t('common.with') }}</span>

    <template v-for="setting in settings" :key="setting">
      <n-tag size="small">
        <template #icon>
          <n-icon class="translucent" :component="SettingsIcon" />
        </template>
        {{ setting }}
      </n-tag>
    </template>
  </n-flex>
</template>
