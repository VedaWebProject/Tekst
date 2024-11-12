<script setup lang="ts">
import type { TextAnnotationResourceConfig } from '@/api';
import { NFormItem, NInput } from 'naive-ui';
import { typeSpecificResourceConfigFormRules } from '@/forms/formRules';

const model = defineModel<TextAnnotationResourceConfig['multiValueDelimiter']>();
</script>

<template>
  <!-- MULTI VALUE DELIMITER -->
  <h5 style="margin-top: 0">
    {{ $t('resources.settings.config.multiValueDelimiter') }}
  </h5>
  <n-form-item
    :show-label="false"
    :rule="typeSpecificResourceConfigFormRules.textAnnotation.multiValueDelimiter"
    path="config.multiValueDelimiter"
  >
    <n-input v-model:value="model" />
  </n-form-item>
</template>
