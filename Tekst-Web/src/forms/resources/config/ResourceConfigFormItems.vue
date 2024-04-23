<script setup lang="ts">
import type { AnyResourceConfig } from '@/api';
import { generalConfigFormItems, specialConfigFormItems } from '@/forms/resources/config/mappings';
import CommonResourceConfigFormItems from '@/forms/resources/config/CommonResourceConfigFormItems.vue';

defineProps<{
  resourceType: string;
  loading?: boolean;
}>();

const model = defineModel<AnyResourceConfig>({ default: {} });

function handleUpdateGeneralConfig(field: string, value: any) {
  model.value = {
    ...model.value,
    general: {
      ...model.value?.general,
      [field]: value,
    },
  };
}

function handleUpdateSpecialConfig(field: string, value: any) {
  model.value = {
    ...model.value,
    [field]: value,
  };
}
</script>

<template>
  <h3>{{ $t('resources.settings.config.heading') }}</h3>

  <!-- COMMON RESOURCE CONFIG -->
  <common-resource-config-form-items
    v-if="model?.common"
    :model="model.common"
    @update:model="(u: any) => (model = { ...model, common: u })"
  />

  <!-- GENERAL RESOURCE TYPE-SPECIFIC CONFIG -->
  <h4>
    {{ $t('resources.types.' + resourceType + '.label') }}
  </h4>
  <h5>
    {{ $t('general.general') }}
  </h5>
  <template v-for="(configValue, key) in model?.general" :key="key">
    <component
      :is="generalConfigFormItems[key]"
      v-if="key in generalConfigFormItems"
      :model-value="configValue"
      @update:model-value="(u: any) => handleUpdateGeneralConfig(key, u)"
    />
  </template>

  <!-- SPECIAL RESOURCE TYPE-SPECIFIC CONFIG -->
  <template v-for="(configModel, key) in model" :key="key">
    <component
      :is="specialConfigFormItems[key]"
      v-if="key in specialConfigFormItems"
      :model-value="configModel"
      @update:model-value="(u: any) => handleUpdateSpecialConfig(key, u)"
    />
  </template>
</template>
