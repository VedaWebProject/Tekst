<script setup lang="ts">
import type { TextRead } from '@/openapi';
import { computed } from 'vue';
import { useStateStore, usePlatformStore } from '@/stores';
import { useRouter } from 'vue-router';
import { NDropdown, NButton, NIcon } from 'naive-ui';
import ArrowDropDownFilled from '@vicons/material/ArrowDropDownFilled';

const router = useRouter();
const state = useStateStore();
const pf = usePlatformStore();

const availableTexts = pf.data?.texts;
const options = computed(() =>
  availableTexts
    ?.filter((t: TextRead) => t.id !== state.text?.id)
    .map((t: TextRead) => ({
      label: t.title,
      key: t.slug,
    }))
);

function handleSelect(key: string) {
  if ('text' in router.currentRoute.value.params) {
    router.push({
      name: router.currentRoute.value.name || 'browse',
      params: { ...router.currentRoute.value.params, text: key },
    });
  } else {
    state.text = availableTexts?.find((t) => t.slug === key);
  }
}
</script>

<template>
  <n-dropdown
    v-if="state.text"
    trigger="click"
    :options="options"
    placement="bottom-start"
    @select="handleSelect"
  >
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
      {{ state.text.title }}
    </n-button>
  </n-dropdown>
</template>
