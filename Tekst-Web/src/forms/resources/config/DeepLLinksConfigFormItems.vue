<script setup lang="ts">
import { deeplSourceLanguages, type DeepLLinksConfig } from '@/api';
import LabelledSwitch from '@/components/LabelledSwitch.vue';
import { NFormItem, NSelect } from 'naive-ui';

const model = defineModel<DeepLLinksConfig>({ required: true });

const languageOptions = deeplSourceLanguages.map((l) => ({ label: l, value: l }));

function handleUpdate(field: string, value: unknown) {
  model.value = {
    ...model.value,
    [field]: value,
  };
}
</script>

<template>
  <h5 style="margin-top: 0">
    {{ $t('resources.settings.config.deeplLinks.heading') }}
  </h5>

  <!-- ENABLED -->
  <n-form-item :show-label="false">
    <labelled-switch
      :model-value="model.enabled"
      :label="$t('resources.settings.config.enabled')"
      @update:model-value="(v) => handleUpdate('enabled', v)"
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
</template>
