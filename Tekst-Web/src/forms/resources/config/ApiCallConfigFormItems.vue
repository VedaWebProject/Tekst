<script setup lang="ts">
import type { AnyResourceRead } from '@/api';
import type { components } from '@/api/schema';
import FormSectionHeading from '@/components/FormSectionHeading.vue';
import { typeSpecificResourceConfigFormRules } from '@/forms/formRules';
import { NFormItem, NInput, NSelect } from 'naive-ui';

defineProps<{ resource: AnyResourceRead }>();
const model = defineModel<components['schemas']['ApiCallConfig']>({
  required: true,
});

const methodOptions = ['GET', 'POST', 'QUERY', 'SEARCH'].map((m) => ({
  label: m,
  value: m,
}));
</script>

<template>
  <form-section-heading :label="$t('resources.settings.config.apiCall.heading')" />

  <!-- ENDPOINT URL -->
  <n-form-item
    path="config.special.apiCall.endpoint"
    :label="$t('resources.settings.config.apiCall.endpoint')"
    :rule="typeSpecificResourceConfigFormRules['apiCall'].endpoint"
  >
    <n-input
      v-model:value="model.endpoint"
      type="text"
      :placeholder="$t('resources.settings.config.apiCall.endpoint')"
      @keydown.enter.prevent
    />
  </n-form-item>

  <!-- HTTP METHOD -->
  <n-form-item
    path="config.special.apiCall.method"
    :label="$t('resources.settings.config.apiCall.method')"
  >
    <n-select v-model:value="model.method" :options="methodOptions" />
  </n-form-item>

  <!-- REQUEST BODY CONTENT TYPE -->
  <n-form-item
    path="config.special.apiCall.contentType"
    :label="$t('resources.settings.config.apiCall.contentType')"
    :rule="typeSpecificResourceConfigFormRules['apiCall'].contentType"
  >
    <n-input
      v-model::value="model.contentType"
      type="text"
      :placeholder="$t('resources.settings.config.apiCall.contentType')"
      :disabled="model.method === 'GET'"
      @keydown.enter.prevent
    />
  </n-form-item>
</template>
