<script setup lang="ts">
import type { AnyResourceConfig } from '@/api';
import { generalConfigFormItems, specialConfigFormItems } from '@/forms/resources/mappings';
import CommonResourceConfigFormItems from './CommonResourceConfigFormItems.vue';

const props = withDefaults(
  defineProps<{
    model?: AnyResourceConfig;
    resourceType: string;
    loading?: boolean;
  }>(),
  {
    model: () => ({}),
  }
);

const emit = defineEmits(['update:model']);

function handleUpdateGeneralConfig(field: string, value: any) {
  emit('update:model', {
    ...props.model,
    general: {
      ...props.model.general,
      [field]: value,
    },
  });
}

function handleUpdateSpecialConfig(field: string, value: any) {
  emit('update:model', {
    ...props.model,
    [field]: value,
  });
}
</script>

<template>
  <h3>{{ $t('resources.settings.config.heading') }}</h3>

  <!-- COMMON RESOURCE CONFIG -->
  <common-resource-config-form-items
    v-if="model.common"
    :model="model.common"
    @update:model="(u: any) => $emit('update:model', { ...model, common: u })"
  />

  <!-- GENERAL RESOURCE TYPE-SPECIFIC CONFIG -->
  <h4>
    {{ $t('resources.types.' + resourceType + '.label') }}
  </h4>
  <template v-for="(configValue, key) in model.general" :key="key">
    <component
      :is="generalConfigFormItems[key]"
      v-if="key in generalConfigFormItems"
      :value="configValue"
      @update:value="(u: any) => handleUpdateGeneralConfig(key, u)"
    />
  </template>

  <!-- SPECIAL RESOURCE TYPE-SPECIFIC CONFIG -->
  <template v-for="(configModel, key) in model" :key="key">
    <component
      :is="specialConfigFormItems[key]"
      v-if="key in specialConfigFormItems"
      :model="configModel"
      @update:model="(u: any) => handleUpdateSpecialConfig(key, u)"
    />
  </template>
</template>
