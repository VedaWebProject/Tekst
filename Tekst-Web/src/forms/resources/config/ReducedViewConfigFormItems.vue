<script setup lang="ts">
import type { components } from '@/api/schema';
import FormSectionHeading from '@/components/FormSectionHeading.vue';
import LabeledSwitch from '@/components/LabeledSwitch.vue';
import { reducedViewConfigFormRules } from '@/forms/formRules';
import { NFormItem, NInput } from 'naive-ui';

const model = defineModel<components['schemas']['ReducedViewConfig']>({ required: true });
</script>

<template>
  <form-section-heading :label="$t('resources.settings.config.reducedView.heading')" />
  <!-- DISPLAY AS SINGLE LINE -->
  <n-form-item :show-label="false">
    <labeled-switch v-model="model.singleLine" />
  </n-form-item>
  <!-- SINGLE LINE DELIMITER -->
  <n-form-item
    :label="$t('resources.settings.config.reducedView.lineDelimiter')"
    :rule="reducedViewConfigFormRules.singleLineDelimiter"
    path="config.general.reducedView.singleLineDelimiter"
  >
    <n-input v-model:value="model.singleLineDelimiter" :disabled="!model.singleLine" />
  </n-form-item>
</template>
