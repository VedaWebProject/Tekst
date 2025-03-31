<script setup lang="ts">
import { deeplSourceLanguages, type AnyResourceRead } from '@/api';
import type { components } from '@/api/schema';
import FormSectionHeading from '@/components/FormSectionHeading.vue';
import LabeledSwitch from '@/components/LabeledSwitch.vue';
import { $t } from '@/i18n';
import { NFormItem, NSelect } from 'naive-ui';

defineProps<{ resource: AnyResourceRead }>();
const model = defineModel<components['schemas']['DeepLLinksConfig']>({
  required: true,
});

const languageOptions = deeplSourceLanguages.map((l) => ({ label: l, value: l }));
</script>

<template>
  <form-section-heading :label="$t('resources.settings.config.plainText.deeplLinks.heading')" />

  <!-- enabled -->
  <n-form-item :show-label="false">
    <labeled-switch v-model="model.enabled" />
  </n-form-item>

  <!-- source language -->
  <n-form-item :label="$t('resources.settings.config.plainText.deeplLinks.sourceLanguage')">
    <n-select
      v-model:value="model.sourceLanguage"
      :disabled="!model.enabled"
      :options="languageOptions"
    />
  </n-form-item>
</template>
