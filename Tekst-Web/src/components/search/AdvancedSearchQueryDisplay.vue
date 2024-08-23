<script setup lang="ts">
import type { AdvancedSearchRequestBody } from '@/api';
import { usePlatformData } from '@/composables/platformData';
import { computed } from 'vue';
import { NFlex, NTag, NIcon } from 'naive-ui';
import { useResourcesStore, useStateStore, useThemeStore } from '@/stores';
import { $t } from '@/i18n';
import { ResourceIcon, SettingsIcon } from '@/icons';
import { pickTranslation } from '@/utils';

const props = defineProps<{
  req: AdvancedSearchRequestBody;
}>();

const state = useStateStore();
const { pfData } = usePlatformData();
const theme = useThemeStore();
const resources = useResourcesStore();

const neutralTagColor = { color: 'var(--main-bg-color)' };

const searchedResources = computed(() => {
  return props.req.q.map((q) => {
    const res = resources.all.find((r) => r.id === q.cmn.res);
    return {
      id: q.cmn.res,
      label: pickTranslation(res?.title, state.locale),
      color: theme.getAccentColors(res?.textId).fade4 || neutralTagColor.color,
      required: q.cmn.req,
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
    <span class="b">{{ searchLabel }}</span>
    <span>{{ $t('general.in') }}</span>

    <template v-for="(r, index) in searchedResources" :key="`${index}-${r.id}`">
      <n-tag v-if="!!r" :color="{ color: r.color }" :bordered="false" size="small">
        <template #icon>
          <n-icon class="translucent" :component="ResourceIcon" />
        </template>
        {{ r.label }}
        {{ r.required ? ` (${$t('search.advancedSearch.required')})` : '' }}
      </n-tag>
    </template>

    <span v-if="!!settings.length">{{ $t('general.with') }}</span>

    <template v-for="setting in settings" :key="setting">
      <n-tag :color="neutralTagColor" :bordered="false" size="small">
        <template #icon>
          <n-icon class="translucent" :component="SettingsIcon" />
        </template>
        {{ setting }}
      </n-tag>
    </template>
  </n-flex>
</template>
