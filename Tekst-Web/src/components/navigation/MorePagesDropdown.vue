<script setup lang="ts">
import { NButton, NIcon, NDropdown } from 'naive-ui';
import ExpandMoreOutlined from '@vicons/material/ExpandMoreOutlined';
import { usePlatformData } from '@/platformData';
import { useStateStore } from '@/stores';
import { computed } from 'vue';
import type { ClientSegmentHead } from '@/api';

const { pfData } = usePlatformData();
const state = useStateStore();

const options = computed(() => {
  let ids: ClientSegmentHead[] = [];
  // add pages with current locale
  ids = ids.concat(pfData.value?.pagesInfo.filter((p) => p.locale === state.locale) || []);
  // add pages without locale
  ids = ids.concat(
    pfData.value?.pagesInfo.filter((p) => !p.locale && !ids.find((i) => i.key === p.key)) || []
  );
  // add pages with enUS locale (fallback)
  ids = ids.concat(
    pfData.value?.pagesInfo.filter(
      (p) => p.locale === 'enUS' && !ids.find((i) => i.key === p.key)
    ) || []
  );
  return ids.map((p) => ({ label: p.title, key: p.key }));
});
</script>

<template>
  <n-dropdown
    v-if="!!options.length"
    ref="textSelectDropdownRef"
    trigger="click"
    :options="options"
    placement="bottom"
    :size="state.dropdownSize"
    show-arrow
    @select="(key: string) => $router.push({ name: 'page', query: { p: key } })"
  >
    <n-button
      text
      icon-placement="right"
      class="navbar-more"
      style="
        padding-left: var(--layout-gap);
        padding-right: var(--layout-gap);
        font-weight: var(--app-ui-font-weight-normal);
      "
    >
      {{ $t('nav.more') }}
      <template #icon>
        <n-icon :component="ExpandMoreOutlined" />
      </template>
    </n-button>
  </n-dropdown>
</template>
