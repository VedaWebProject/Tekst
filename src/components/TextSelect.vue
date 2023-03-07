<script setup lang="ts">
import type { TextRead } from '@/openapi';
import { computed, h } from 'vue';
import { useStateStore, usePlatformStore } from '@/stores';
import { useRouter } from 'vue-router';
import { NDropdown, NButton, NIcon } from 'naive-ui';
import ArrowDropDownFilled from '@vicons/material/ArrowDropDownFilled';
import TextSelectOption from './TextSelectOption.vue';

const router = useRouter();
const state = useStateStore();
const pf = usePlatformStore();
const availableTexts = pf.data?.texts || [];

function renderLabel(title: string, subtitle?: string, accentColor?: string) {
  return h(TextSelectOption, { title, subtitle, accentColor });
}

const options = computed(() =>
  availableTexts.map((t: TextRead) => ({
    label: () => renderLabel(t.title, t.subtitle, t.accentColor),
    key: t.slug,
    disabled: t.id === state.text?.id,
  }))
);

function handleSelect(key: string) {
  if ('text' in router.currentRoute.value.params) {
    router.push({
      name: router.currentRoute.value.name || 'browse',
      params: { ...router.currentRoute.value.params, text: key },
    });
  } else {
    state.text = availableTexts.find((t) => t.slug === key);
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

<style scoped>
.text-select-option-indicator {
  width: 20px;
  height: 20px;
  border-radius: 50%;
}
</style>
