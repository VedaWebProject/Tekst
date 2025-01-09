<script setup lang="ts">
import type { QuickSearchRequestBody } from '@/api';
import { usePlatformData } from '@/composables/platformData';
import { $t } from '@/i18n';
import { SearchIcon, SettingsIcon, TextsIcon } from '@/icons';
import { useThemeStore } from '@/stores';
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

const { pfData } = usePlatformData();
const theme = useThemeStore();

const targetTexts = computed(() => {
  return (pfData.value?.texts.filter((t) => props.req.qck?.txt?.includes(t.id)) || []).map((t) => ({
    ...t,
    color: theme.getAccentColors(t.id).base,
    colorFade: theme.getAccentColors(t.id).fade3,
  }));
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
    <span v-if="!loading && total != null && totalRelation">
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

    <n-tag class="b content-font" size="small">
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
      :color="{ borderColor: text.colorFade, textColor: text.color }"
      size="small"
    >
      <template #icon>
        <n-icon class="translucent" :component="TextsIcon" />
      </template>
      {{ text.title }}
    </n-tag>

    <span v-if="!!settings.length">{{ $t('general.with') }}</span>

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
