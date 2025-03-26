<script setup lang="ts">
import FormSectionHeading from '@/components/FormSectionHeading.vue';
import { useStateStore } from '@/stores';
import { NFormItem, NSelect, type SelectOption } from 'naive-ui';
import { computed, h } from 'vue';

const model = defineModel<string>();
const state = useStateStore();

const options = computed(() =>
  [...(state.pf?.state.fonts || []), 'Tekst Content Font', 'Tekst UI Font']?.map((f) => ({
    label: f,
    value: f,
  }))
);

function renderLabel(option: SelectOption) {
  return h(
    'div',
    {
      style: `font-family: '${option.value}', 'Tekst Content Font', serif;`,
    },
    option.label as string
  );
}
</script>

<template>
  <form-section-heading :label="$t('resources.settings.config.general.font')" />
  <n-form-item v-if="options.length" :show-label="false">
    <n-select
      v-model:value="model"
      clearable
      :options="options"
      :placeholder="$t('common.default')"
      :render-label="renderLabel"
    />
  </n-form-item>
</template>
