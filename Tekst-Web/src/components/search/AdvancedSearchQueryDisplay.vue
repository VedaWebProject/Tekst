<script setup lang="ts">
import type { AdvancedSearchRequestBody } from '@/api';
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
const theme = useThemeStore();
const resources = useResourcesStore();

const searchedResources = computed(() => {
  const qRes = [...new Set(props.req.q?.map((q) => q.cmn.res))];
  return resources.all
    .filter((r) => qRes.includes(r.id))
    .map((r) => {
      return {
        id: r.id,
        label: pickTranslation(r.title, state.locale),
        color: theme.getTextColors(r.textId).base,
        colorFade: theme.getTextColors(r.textId).fade3,
      };
    });
});

const searchLabel = computed(
  () => pickTranslation(state.pf?.state.navSearchEntry, state.locale) || $t('common.search')
);

const settings = computed(() => [
  ...(props.req.gen?.strict ? [$t('search.settings.general.strict')] : []),
]);
</script>

<template>
  <n-flex align="center" class="text-tiny" :size="[4, 8]">
    <template v-if="!loading && total != null && totalRelation">
      <span>
        {{ searchLabel }}:
        {{ totalRelation === 'eq' ? '' : '≥' }}
        <b>{{ $t('search.results.count', { count: total }) }}</b>
      </span>
    </template>
    <span v-else>
      {{ $t('search.results.searching') }}
    </span>

    <span>{{ $t('common.in') }}</span>

    <n-tag
      v-for="(r, index) in searchedResources"
      :key="`${index}-${r.id}`"
      :color="{ borderColor: r.colorFade, textColor: r.color }"
      size="small"
    >
      <template #icon>
        <n-icon class="translucent" :component="ResourceIcon" />
      </template>
      {{ r.label }}
    </n-tag>

    <span v-if="!!settings.length">{{ $t('common.with') }}</span>

    <n-tag v-for="setting in settings" :key="setting" size="small">
      <template #icon>
        <n-icon class="translucent" :component="SettingsIcon" />
      </template>
      {{ setting }}
    </n-tag>
  </n-flex>
</template>
