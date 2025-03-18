<script setup lang="ts">
import type { AnyResourceConfig, AnyResourceRead } from '@/api';
import { specialConfigFormItems } from '@/forms/resources/config/mappings';

defineProps<{
  resource: AnyResourceRead;
}>();

const model = defineModel<AnyResourceConfig>({ required: true });
</script>

<template>
  <!-- SPECIAL RESOURCE TYPE-SPECIFIC CONFIG -->
  <template v-for="(_, key) in model" :key="key">
    <component
      v-model="model[key]"
      :is="specialConfigFormItems[key]"
      v-if="key in specialConfigFormItems"
      :resource="resource"
    />
  </template>
</template>
