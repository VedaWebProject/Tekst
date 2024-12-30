<script setup lang="ts">
import type { LineLabellingConfig } from '@/api';
import LabelledSwitch from '@/components/LabelledSwitch.vue';
import { $t } from '@/i18n';
import { NFormItem, NSelect } from 'naive-ui';
import { computed } from 'vue';

const model = defineModel<LineLabellingConfig>({ required: true });

const labellingOptions = computed(() =>
  ['numbersZeroBased', 'numbersOneBased', 'lettersLowercase', 'lettersUppercase'].map((o) => ({
    label: $t(`resources.settings.config.lineLabelling.${o}`),
    value: o,
  }))
);

function handleUpdate(field: string, value: unknown) {
  model.value = {
    ...model.value,
    [field]: value,
  };
}
</script>

<template>
  <h5 style="margin-top: 0">
    {{ $t('resources.settings.config.lineLabelling.heading') }}
  </h5>

  <!-- ENABLED -->
  <n-form-item :show-label="false">
    <labelled-switch
      :model-value="model.enabled"
      :label="$t('resources.settings.config.enabled')"
      @update:model-value="(v) => handleUpdate('enabled', v)"
    />
  </n-form-item>

  <!-- LABELLING TYPE -->
  <n-form-item :label="$t('general.type')">
    <n-select
      :disabled="!model.enabled"
      :value="model.labellingType"
      :options="labellingOptions"
      @update:value="(v) => handleUpdate('labellingType', v)"
    />
  </n-form-item>
</template>
