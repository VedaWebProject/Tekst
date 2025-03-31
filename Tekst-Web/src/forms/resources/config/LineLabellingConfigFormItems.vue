<script setup lang="ts">
import type { AnyResourceRead } from '@/api';
import type { components } from '@/api/schema';
import FormSectionHeading from '@/components/FormSectionHeading.vue';
import LabeledSwitch from '@/components/LabeledSwitch.vue';
import { $t } from '@/i18n';
import { NFormItem, NSelect } from 'naive-ui';
import { computed } from 'vue';

defineProps<{ resource: AnyResourceRead }>();
const model = defineModel<components['schemas']['LineLabellingConfig']>({
  required: true,
});

const labellingOptions = computed(() =>
  ['numbersZeroBased', 'numbersOneBased', 'lettersLowercase', 'lettersUppercase'].map((o) => ({
    label: $t(`resources.settings.config.plainText.lineLabelling.${o}`),
    value: o,
  }))
);
</script>

<template>
  <form-section-heading :label="$t('resources.settings.config.plainText.lineLabelling.heading')" />

  <!-- enabled -->
  <n-form-item :show-label="false">
    <labeled-switch v-model="model.enabled" />
  </n-form-item>

  <!-- labelling type -->
  <n-form-item :label="$t('common.type')">
    <n-select
      v-model:value="model.labellingType"
      :disabled="!model.enabled"
      :options="labellingOptions"
    />
  </n-form-item>
</template>
