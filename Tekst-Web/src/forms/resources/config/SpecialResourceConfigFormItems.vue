<script setup lang="ts">
import type { AnyResourceConfig } from '@/api';
import { generalConfigFormItems, specialConfigFormItems } from '@/forms/resources/config/mappings';

defineProps<{
  resourceType: string;
  loading?: boolean;
}>();

const model = defineModel<AnyResourceConfig>({ required: true });
</script>

<template>
  <template v-for="(_, key) in model.general" :key="key">
    <component
      v-model="model.general[key]"
      :is="generalConfigFormItems[key]"
      v-if="key in generalConfigFormItems"
    />
  </template>

  <!-- SPECIAL RESOURCE TYPE-SPECIFIC CONFIG -->
  <template v-for="(_, key) in model" :key="key">
    <component
      v-model="model[key]"
      :is="specialConfigFormItems[key]"
      v-if="key in specialConfigFormItems"
    />
  </template>
</template>
