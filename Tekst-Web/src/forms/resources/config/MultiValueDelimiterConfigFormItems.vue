<script setup lang="ts">
import type { TextAnnotationResourceConfig } from '@/api';
import { typeSpecificResourceConfigFormRules } from '@/forms/formRules';
import { NFormItem, NInput } from 'naive-ui';

const model = defineModel<TextAnnotationResourceConfig['multiValueDelimiter']>();
</script>

<template>
  <!-- MULTI VALUE DELIMITER -->
  <n-form-item
    :label="$t('resources.settings.config.multiValueDelimiter')"
    :rule="typeSpecificResourceConfigFormRules.textAnnotation.multiValueDelimiter"
    path="config.multiValueDelimiter"
  >
    <n-input v-model:value="model" />
  </n-form-item>
</template>
