<script setup lang="ts">
import type { TextAnnotationResourceConfig } from '@/api';
import { NFormItem, NInput } from 'naive-ui';
import { typeSpecificResourceConfigFormRules } from '@/forms/formRules';
import IconHeading from '@/components/generic/IconHeading.vue';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';

defineProps<{
  model: TextAnnotationResourceConfig['displayTemplate'];
}>();

const emit = defineEmits(['update:model']);
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
    <n-input
      :value="model"
      type="textarea"
      rows="3"
      style="font-family: monospace"
      @update:value="(v) => emit('update:model', v)"
    />
  </n-form-item>
</template>
