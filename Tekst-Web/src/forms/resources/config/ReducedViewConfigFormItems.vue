<script setup lang="ts">
import { NFormItem, NInput } from 'naive-ui';
import { reducedViewConfigFormRules } from '@/forms/formRules';
import type { components } from '@/api/schema';
import LabelledSwitch from '@/components/LabelledSwitch.vue';

const model = defineModel<components['schemas']['ReducedViewConfig']>({ required: true });
</script>

<template>
  <h5>{{ $t('resources.settings.config.reducedView.heading') }}</h5>
  <!-- DISPLAY AS SINGLE LINE -->
  <n-form-item :show-label="false">
    <labelled-switch
      v-model="model.singleLine"
      :label="$t('resources.settings.config.reducedView.singleLine')"
    />
  </n-form-item>
  <!-- SINGLE LINE DELIMITER -->
  <n-form-item
    :label="$t('resources.settings.config.reducedView.singleLineDelimiter')"
    :rule="reducedViewConfigFormRules.singleLineDelimiter"
    path="config.general.reducedView.singleLineDelimiter"
  >
    <n-input v-model:value="model.singleLineDelimiter" :disabled="!model.singleLine" />
  </n-form-item>
</template>
