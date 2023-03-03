<script setup lang="ts">
import type { TextRead } from '@/openapi';
import { useStateStore, usePlatformStore } from '@/stores';
import { NDropdown, NButton, NIcon } from 'naive-ui';
import ArrowDropDownFilled from '@vicons/material/ArrowDropDownFilled';

const state = useStateStore();
const pf = usePlatformStore();

const availableTexts = pf.data?.texts;
const options = availableTexts?.map((t: TextRead) => ({
  label: t.title,
  key: t.id,
}));

function handleSelect(key: string) {
  state.text = availableTexts?.find((t) => t.id === key);
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
