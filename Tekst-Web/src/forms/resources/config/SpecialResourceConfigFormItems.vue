<script setup lang="ts">
import type { AnyResourceConfig } from '@/api';
import { specialConfigFormItems } from '@/forms/resources/config/mappings';

defineProps<{
  resourceType: string;
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
    />
  </template>
</template>
