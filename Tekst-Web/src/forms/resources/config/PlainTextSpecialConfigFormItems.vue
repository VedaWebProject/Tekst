<script setup lang="ts">
import { deeplSourceLanguages } from '@/api';
import type { components } from '@/api/schema';
import LabelledSwitch from '@/components/LabelledSwitch.vue';
import { $t } from '@/i18n';
import { NFormItem, NSelect } from 'naive-ui';
import { computed } from 'vue';

const model = defineModel<components['schemas']['PlainTextSpecialConfig']>({
  required: true,
});

const labellingOptions = computed(() =>
  ['numbersZeroBased', 'numbersOneBased', 'lettersLowercase', 'lettersUppercase'].map((o) => ({
    label: $t(`resources.settings.config.plainText.lineLabelling.${o}`),
    value: o,
  }))
);

const languageOptions = deeplSourceLanguages.map((l) => ({ label: l, value: l }));
</script>

<template>
  <!-- LINE LABELLING -->

  <h5 style="margin-top: 0">
    {{ $t('resources.settings.config.plainText.lineLabelling.heading') }}
  </h5>

  <!-- enabled -->
  <n-form-item :show-label="false">
    <labelled-switch
      v-model="model.lineLabelling.enabled"
      :label="$t('resources.settings.config.enabled')"
    />
  </n-form-item>

  <!-- labelling type -->
  <n-form-item :label="$t('general.type')">
    <n-select
      v-model:value="model.lineLabelling.labellingType"
      :disabled="!model.lineLabelling.enabled"
      :options="labellingOptions"
    />
  </n-form-item>

  <!-- DEEPL LINKS -->

  <h5 style="margin-top: 0">
    {{ $t('resources.settings.config.plainText.deeplLinks.heading') }}
  </h5>

  <!-- enabled -->
  <n-form-item :show-label="false">
    <labelled-switch
      v-model="model.deeplLinks.enabled"
      :label="$t('resources.settings.config.enabled')"
    />
  </n-form-item>

  <!-- source language -->
  <n-form-item :label="$t('resources.settings.config.plainText.deeplLinks.sourceLanguage')">
    <n-select
      v-model:value="model.deeplLinks.sourceLanguage"
      :disabled="!model.deeplLinks.enabled"
      :options="languageOptions"
    />
  </n-form-item>
</template>
