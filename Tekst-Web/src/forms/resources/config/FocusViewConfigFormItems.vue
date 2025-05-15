<script setup lang="ts">
import type { AnyResourceRead } from '@/api';
import type { components } from '@/api/schema';
import FormSection from '@/components/FormSection.vue';
import LabeledSwitch from '@/components/LabeledSwitch.vue';
import { focusViewConfigFormRules } from '@/forms/formRules';
import { NFormItem, NInput } from 'naive-ui';

defineProps<{ resource: AnyResourceRead }>();
const model = defineModel<components['schemas']['FocusViewConfig']>({ required: true });
</script>

<template>
  <form-section :title="$t('resources.settings.config.focusView.heading')">
    <!-- DISPLAY AS SINGLE LINE -->
    <n-form-item :show-label="false">
      <labeled-switch v-model="model.singleLine" />
    </n-form-item>
    <!-- SINGLE LINE DELIMITER -->
    <n-form-item
      :label="$t('resources.settings.config.focusView.delimiter')"
      :rule="focusViewConfigFormRules.delimiter"
      path="config.special.focusView.delimiter"
    >
      <n-input v-model:value="model.delimiter" :disabled="!model.singleLine" />
    </n-form-item>
  </form-section>
</template>
