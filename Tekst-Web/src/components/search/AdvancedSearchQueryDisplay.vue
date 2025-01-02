<script setup lang="ts">
import type { AdvancedSearchRequestBody } from '@/api';
import { usePlatformData } from '@/composables/platformData';
import { $t } from '@/i18n';
import { ResourceIcon, SettingsIcon } from '@/icons';
import { useResourcesStore, useStateStore, useThemeStore } from '@/stores';
import { pickTranslation } from '@/utils';
import { NFlex, NIcon, NTag } from 'naive-ui';
import { computed } from 'vue';

const props = withDefaults(
  defineProps<{
    req: AdvancedSearchRequestBody;
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
const { pfData } = usePlatformData();
const theme = useThemeStore();
const resources = useResourcesStore();

const neutralTagColor = { color: 'var(--main-bg-color)' };

const searchedResources = computed(() => {
  const qRes = [...new Set(props.req.q?.map((q) => q.cmn.res))];
  return resources.all
    .filter((r) => qRes.includes(r.id))
    .map((r) => {
      return {
        id: r.id,
        label: pickTranslation(r.title, state.locale),
        color: theme.getAccentColors(r.textId).fade4,
      };
    });
});

const searchLabel = computed(
  () => pickTranslation(pfData.value?.state.navSearchEntry, state.locale) || $t('nav.search')
);

const settings = computed(() => [
  ...(props.req.gen?.strict ? [$t('search.settings.general.strict')] : []),
]);
</script>

<template>
  <n-flex align="center" class="text-tiny" :size="[4, 8]">
    <template v-if="!loading && total != null && totalRelation">
      <span>
        {{ totalRelation === 'eq' ? '' : '≥' }}
        {{
          $t('search.results.count', {
            count: total,
          })
        }}
        {{ $t('general.for') }}
      </span>
      <span class="b">{{ searchLabel }}</span>
    </template>
    <span v-else>
      {{ $t('search.results.searching') }}
    </span>

    <span>{{ $t('general.in') }}</span>

    <n-tag
      v-for="(r, index) in searchedResources"
      :key="`${index}-${r.id}`"
      :color="{ color: r.color }"
      :bordered="false"
      size="small"
    >
      <template #icon>
        <n-icon class="translucent" :component="ResourceIcon" />
      </template>
      {{ r.label }}
    </n-tag>

    <span v-if="!!settings.length">{{ $t('general.with') }}</span>

    <n-tag
      v-for="setting in settings"
      :key="setting"
      :color="neutralTagColor"
      :bordered="false"
      size="small"
    >
      <template #icon>
        <n-icon class="translucent" :component="SettingsIcon" />
      </template>
      {{ setting }}
    </n-tag>
  </n-flex>
</template>
