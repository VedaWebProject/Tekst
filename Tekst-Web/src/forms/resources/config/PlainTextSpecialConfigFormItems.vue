<script setup lang="ts">
import { deeplSourceLanguages, type PlainTextResourceRead } from '@/api';
import type { components } from '@/api/schema';
import FormSectionHeading from '@/components/FormSectionHeading.vue';
import LabeledSwitch from '@/components/LabeledSwitch.vue';
import { $t } from '@/i18n';
import { NFormItem, NSelect } from 'naive-ui';
import { computed } from 'vue';

defineProps<{ resource: PlainTextResourceRead }>();

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

  <form-section-heading :label="$t('resources.settings.config.plainText.lineLabelling.heading')" />

  <!-- enabled -->
  <n-form-item :show-label="false">
    <labeled-switch v-model="model.lineLabelling.enabled" />
  </n-form-item>

  <!-- labelling type -->
  <n-form-item :label="$t('common.type')">
    <n-select
      v-model:value="model.lineLabelling.labellingType"
      :disabled="!model.lineLabelling.enabled"
      :options="labellingOptions"
    />
  </n-form-item>

  <!-- DEEPL LINKS -->

  <form-section-heading :label="$t('resources.settings.config.plainText.deeplLinks.heading')" />

  <!-- enabled -->
  <n-form-item :show-label="false">
    <labeled-switch v-model="model.deeplLinks.enabled" />
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
