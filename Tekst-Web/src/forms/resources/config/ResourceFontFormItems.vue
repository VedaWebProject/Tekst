<script setup lang="ts">
import { usePlatformData } from '@/composables/platformData';
import { NFormItem, NSelect } from 'naive-ui';
import { computed } from 'vue';

const { pfData } = usePlatformData();
const model = defineModel<string>();

const options = computed(() =>
  [...(pfData.value?.state.customFonts || []), 'Tekst Content Font', 'Tekst UI Font']?.map((f) => ({
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
