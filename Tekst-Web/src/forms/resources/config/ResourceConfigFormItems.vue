<script setup lang="ts">
import type { AnyResourceConfig } from '@/api';
import HelpButtonWidget from '@/components/widgets/HelpButtonWidget.vue';
import { NFormItem, NCheckbox } from 'naive-ui';
import specialConfigFormItems from '@/forms/resources/config/special/mappings';

const props = withDefaults(
  defineProps<{
    model?: AnyResourceConfig;
    resourceType: string;
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
  <!-- GENERAL RESOURCE CONFIG -->
  <h3>{{ $t('resources.config.headingConfig') }}</h3>
  <h4>{{ $t('resources.headingGeneral') }}</h4>
  <n-form-item path="showOnParentLevel" :show-label="false" :show-feedback="false">
    <n-checkbox
      :checked="model.showOnParentLevel"
      @update:checked="(u) => handleUpdate('showOnParentLevel', u)"
    >
      {{ $t('resources.config.showOnParentLevel') }}
    </n-checkbox>
    <HelpButtonWidget help-key="resourceConfigCombinedSiblings" />
  </n-form-item>

  <!-- RESOURCE TYPE-SPECIFIC CONFIG -->
  <template v-for="(configModel, key) in model" :key="key">
    <component
      :is="specialConfigFormItems[key]"
      v-if="key in specialConfigFormItems"
      :model="configModel"
      @update:model="(u: any) => handleUpdate(key, u)"
    />
  </template>
</template>
