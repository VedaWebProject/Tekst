<script setup lang="ts">
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
  <n-form-item v-if="options.length" :label="$t('resources.settings.config.general.font')">
    <n-select v-model:value="model" clearable :options="options" />
  </n-form-item>
</template>
