<script setup lang="ts">
import type { TextAnnotationResourceConfig } from '@/api';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import { typeSpecificResourceConfigFormRules } from '@/forms/formRules';
import { NFlex, NFormItem, NInput } from 'naive-ui';

const model = defineModel<TextAnnotationResourceConfig['displayTemplate']>();
</script>

<template>
  <!-- ANNOTATION DISPLAY TEMPLATE -->
  <n-form-item
    :rule="typeSpecificResourceConfigFormRules.textAnnotation.displayTemplate"
    path="config.displayTemplate"
  >
    <template #label>
      <n-flex align="center">
        {{ $t('resources.settings.config.displayTemplate', 2) }}
        <help-button-widget help-key="textAnnotationDisplayTemplate" />
      </n-flex>
    </template>
    <n-input v-model:value="model" type="textarea" rows="3" style="font-family: monospace" />
  </n-form-item>
</template>
