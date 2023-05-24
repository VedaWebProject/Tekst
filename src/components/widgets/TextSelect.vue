<script setup lang="ts">
import type { TextRead } from '@/openapi';
import { computed, h } from 'vue';
import { useStateStore } from '@/stores';
import { useRouter } from 'vue-router';
import { NDropdown, NButton, NIcon } from 'naive-ui';
import ArrowDropDownFilled from '@vicons/material/ArrowDropDownFilled';
import TextSelectOption from '../widgets/TextSelectOption.vue';
import { usePlatformData } from '@/platformData';

const router = useRouter();
const state = useStateStore();
const { pfData } = usePlatformData();
const availableTexts = computed(() => pfData.value?.texts || []);

const renderLabel = (t: TextRead) => {
  return () =>
    h(TextSelectOption, {
      text: t,
      selected: t.id === state.text?.id,
      onClick: handleSelect,
    });
};
const options = computed(() =>
  availableTexts.value
    .filter((t) => t.id !== state.text?.id)
    .map((t: TextRead) => ({
      render: renderLabel(t),
      key: t.slug,
      type: 'render',
      disabled: t.id === state.text?.id,
      props: {
        onClick: () => handleSelect(t.slug),
      },
    }))
);

function handleSelect(key: string) {
  console.log(key);
  if ('text' in router.currentRoute.value.params) {
    router.push({
      name: router.currentRoute.value.name || 'browse',
      params: { ...router.currentRoute.value.params, text: key },
    });
  } else {
    state.text = availableTexts.value.find((t) => t.slug === key);
  }
}
</script>

<template>
  <n-dropdown
    v-if="state.text"
    trigger="click"
    :options="options"
    :disabled="options.length <= 1"
    :render-label="renderLabel"
    placement="bottom-start"
    :size="state.dropdownSize"
    @select="handleSelect"
  >
    <n-button
      text
      icon-placement="right"
      color="#fffe"
      :focusable="false"
      :keyboard="false"
      :title="$t('general.textSelect')"
      :style="{
        fontSize: 'inherit',
        fontWeight: 'var(--app-ui-font-weight-normal)',
        cursor: options.length > 1 ? 'pointer' : 'default',
      }"
    >
      <template #icon v-if="options.length > 1">
        <n-icon>
          <ArrowDropDownFilled />
        </n-icon>
      </template>
      {{ state.text.title }}
    </n-button>
  </n-dropdown>
</template>
