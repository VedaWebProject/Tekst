<script setup lang="ts">
import type { TextAnnotationResourceConfig } from '@/api';
import { NFormItem, NInput } from 'naive-ui';
import { typeSpecificResourceConfigFormRules } from '@/forms/formRules';
import IconHeading from '@/components/generic/IconHeading.vue';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';

const model = defineModel<TextAnnotationResourceConfig['displayTemplate']>();
</script>

<template>
  <!-- DISPLAY TEMPLATE -->
  <icon-heading level="5">
    {{ $t('resources.types.textAnnotation.config.displayTemplate') }}
    <help-button-widget help-key="textAnnotationDisplayTemplate" />
  </icon-heading>
  <n-form-item
    :show-label="false"
    :rule="typeSpecificResourceConfigFormRules.textAnnotation.displayTemplate"
    path="config.displayTemplate"
  >
    <n-input v-model:value="model" type="textarea" rows="3" style="font-family: monospace" />
  </n-form-item>
</template>
