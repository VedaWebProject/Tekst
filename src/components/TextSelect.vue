<script setup lang="ts">
import type { TextRead } from '@/openapi';
import { useStateStore, usePlatformStore } from '@/stores';
import { useRouter } from 'vue-router';
import { NDropdown, NButton, NIcon } from 'naive-ui';
import ArrowDropDownFilled from '@vicons/material/ArrowDropDownFilled';

const router = useRouter();
const state = useStateStore();
const pf = usePlatformStore();

const availableTexts = pf.data?.texts;
const options = availableTexts?.map((t: TextRead) => ({
  label: t.title,
  key: t.slug,
}));

function handleSelect(key: string) {
  router.push({
    path: router.currentRoute.value.path,
    query: { ...router.currentRoute.value.query, text: key },
  });
}
</script>

<template>
  <n-dropdown trigger="click" :options="options" placement="bottom-start" @select="handleSelect">
    <n-button
      text
      icon-placement="right"
      color="#eee"
      :title="$t('general.textSelect')"
      style="font-size: inherit; font-weight: inherit"
    >
      <template #icon>
        <n-icon>
          <ArrowDropDownFilled />
        </n-icon>
      </template>
      {{ state.text?.title || 'Text state not implemented' }}
    </n-button>
  </n-dropdown>
</template>
