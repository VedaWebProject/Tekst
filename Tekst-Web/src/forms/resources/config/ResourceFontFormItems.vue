<script setup lang="ts">
import FormSectionHeading from '@/components/FormSectionHeading.vue';
import { useStateStore } from '@/stores';
import { NFormItem, NSelect } from 'naive-ui';
import { computed } from 'vue';

const model = defineModel<string>();
const state = useStateStore();

const options = computed(() =>
  [...(state.pf?.state.fonts || []), 'Tekst Content Font', 'Tekst UI Font']?.map((f) => ({
    label: f,
    value: f,
  }))
);
</script>

<template>
  <form-section-heading :label="$t('resources.settings.config.general.font')" />
  <n-form-item v-if="options.length" :show-label="false">
    <n-select
      v-model:value="model"
      clearable
      :options="options"
      :placeholder="$t('general.default')"
    />
  </n-form-item>
</template>
