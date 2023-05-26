<script setup lang="ts">
import type { TextRead } from '@/openapi';
import { computed, h, ref } from 'vue';
import { useStateStore } from '@/stores';
import { useRouter } from 'vue-router';
import { NDropdown, NButton, NIcon } from 'naive-ui';
import ArrowDropDownFilled from '@vicons/material/ArrowDropDownFilled';
import TextSelectOption from '../widgets/TextSelectOption.vue';
import { usePlatformData } from '@/platformData';
import { useI18n } from 'vue-i18n';

const router = useRouter();
const state = useStateStore();
const { locale } = useI18n();
const { pfData } = usePlatformData();
const availableTexts = computed(() => pfData.value?.texts || []);
const disabled = computed(() => availableTexts.value.length <= 1);
const textSelectDropdownRef = ref();

const renderLabel = (t: TextRead) => {
  return () =>
    h(TextSelectOption, {
      text: t,
      locale: locale.value,
      selected: t.id === state.text?.id,
      onClick: () => handleSelect(t.slug),
    });
};
const options = computed(() =>
  availableTexts.value.map((t: TextRead) => ({
    render: renderLabel(t),
    key: t.slug,
    type: 'render',
    show: t.id !== state.text?.id,
  }))
);

function handleSelect(key: string) {
  textSelectDropdownRef.value.doUpdateShow(false);
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
    ref="textSelectDropdownRef"
    trigger="click"
    :options="options"
    :disabled="disabled"
    :render-label="renderLabel"
    placement="bottom-start"
    :size="state.dropdownSize"
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
        cursor: !disabled ? 'pointer' : 'default',
      }"
    >
      <template #icon v-if="!disabled">
        <n-icon>
          <ArrowDropDownFilled />
        </n-icon>
      </template>
      {{ state.text.title }}
    </n-button>
  </n-dropdown>
</template>
