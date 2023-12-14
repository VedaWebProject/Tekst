<script setup lang="ts">
import type { AnyLayerConfig } from '@/api';
import HelpButtonWidget from '@/components/widgets/HelpButtonWidget.vue';
import { NFormItem, NCheckbox } from 'naive-ui';
import specialConfigFormItems from '@/forms/layers/config/special/mappings';

const props = withDefaults(
  defineProps<{
    model?: AnyLayerConfig;
    layerType: string;
    loading?: boolean;
  }>(),
  {
    model: () => ({
      showOnParentLevel: false,
    }),
  }
);

const emits = defineEmits(['update:model']);

function handleUpdate(field: string, value: any) {
  emits('update:model', {
    ...props.model,
    [field]: value,
  });
}
</script>

<template>
  <!-- GENERAL LAYER CONFIG -->
  <h3>{{ $t('dataLayers.config.headingConfig') }}</h3>
  <h4>{{ $t('dataLayers.headingGeneral') }}</h4>
  <n-form-item path="showOnParentLevel" :show-label="false" :show-feedback="false">
    <n-checkbox
      :checked="model.showOnParentLevel"
      @update:checked="(u) => handleUpdate('showOnParentLevel', u)"
    >
      {{ $t('dataLayers.config.showOnParentLevel') }}
    </n-checkbox>
    <HelpButtonWidget help-key="dataLayerConfigCombinedSiblings" />
  </n-form-item>

  <!-- LAYER TYPE-SPECIFIC CONFIG -->
  <template v-for="(configModel, key) in model" :key="key">
    <component
      :is="specialConfigFormItems[key]"
      v-if="key in specialConfigFormItems"
      :model="configModel"
      @update:model="(u: any) => handleUpdate(key, u)"
    />
  </template>
</template>
