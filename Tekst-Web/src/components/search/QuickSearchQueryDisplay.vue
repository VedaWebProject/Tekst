<script setup lang="ts">
import type { QuickSearchRequestBody } from '@/api';
import { usePlatformData } from '@/composables/platformData';
import { computed } from 'vue';
import { NFlex, NTag, NIcon } from 'naive-ui';
import { useThemeStore } from '@/stores';
import { $t } from '@/i18n';
import { SearchIcon, SettingsIcon, TextsIcon } from '@/icons';

const props = defineProps<{
  req: QuickSearchRequestBody;
}>();

const { pfData } = usePlatformData();
const theme = useThemeStore();

const neutralTagColor = { color: 'var(--main-bg-color)' };

const targetTexts = computed(() => {
  const qt = (props.req.qck?.txt || [])
    .map((txtId) => pfData.value?.texts.find((txt) => txt.id === txtId))
    .filter((t) => !!t);
  return qt.length ? qt : pfData.value?.texts || [];
});
const settings = computed(() => [
  ...(props.req.qck?.op?.toLowerCase() === 'and'
    ? [$t('search.settings.quick.defaultOperator')]
    : []),
  ...(props.req.gen?.strict ? [$t('search.settings.general.strict')] : []),
]);
</script>

<template>
  <n-flex align="center" class="text-tiny" :size="[4, 8]">
    <n-tag :color="neutralTagColor" :bordered="false" class="b" size="small">
      <template #icon>
        <n-icon class="translucent" :component="SearchIcon" />
      </template>
      {{ req.q }}
    </n-tag>

    {{ $t('general.in') }}

    <template v-for="text in targetTexts" :key="text.id">
      <n-tag
        v-if="text"
        :color="{ color: theme.getAccentColors(text.id).fade4 }"
        :bordered="false"
        size="small"
      >
        <template #icon>
          <n-icon class="translucent" :component="TextsIcon" />
        </template>
        {{ text.title }}
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
