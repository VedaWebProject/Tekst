<script setup lang="ts">
import type { DeepLLinksConfig } from '@/api';
import LabelledSwitch from '@/components/LabelledSwitch.vue';
import { NFormItem, NSelect } from 'naive-ui';

const props = defineProps<{
  model: DeepLLinksConfig;
}>();

const emit = defineEmits(['update:model']);

const languageOptions = [
  'BG',
  'CS',
  'DA',
  'DE',
  'EL',
  'EN',
  'ES',
  'ET',
  'FI',
  'FR',
  'HU',
  'ID',
  'IT',
  'JA',
  'LT',
  'LV',
  'NL',
  'PL',
  'PT',
  'RO',
  'RU',
  'SK',
  'SL',
  'SV',
  'TR',
  'UK',
  'ZH',
].map((l) => ({ label: l, value: l }));

function handleUpdate(field: string, value: any) {
  emit('update:model', {
    ...props.model,
    [field]: value,
  });
}
</script>

<template>
  <h4>
    {{ $t('resources.settings.config.deeplLinks.heading') }}
  </h4>

  <!-- ENABLED -->
  <n-form-item :show-label="false">
    <labelled-switch
      :value="model.enabled"
      :label="$t('resources.settings.config.enabled')"
      @update:value="(v) => handleUpdate('enabled', v)"
    />
  </n-form-item>

  <!-- SOURCE LANGUAGE -->
  <n-form-item :label="$t('resources.settings.config.deeplLinks.sourceLanguage')">
    <n-select
      :disabled="!model.enabled"
      :value="model.sourceLanguage"
      :options="languageOptions"
      @update:value="(v) => handleUpdate('sourceLanguage', v)"
    />
  </n-form-item>

  <!-- TARGET LANGUAGES -->
  <n-form-item
    :label="$t('resources.settings.config.deeplLinks.targetLanguages')"
    :show-feedback="false"
  >
    <n-select
      :disabled="!model.enabled"
      multiple
      :value="model.languages"
      :options="languageOptions"
      @update:value="(v) => handleUpdate('languages', v)"
    />
  </n-form-item>
</template>