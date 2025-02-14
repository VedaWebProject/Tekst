<script setup lang="ts">
import type { AnyResourceConfig } from '@/api';
import { generalConfigFormItems } from '@/forms/resources/config/mappings';

defineProps<{
  resourceType: string;
}>();

const model = defineModel<AnyResourceConfig['general']>({ required: true });
</script>

<template>
  <!-- GENERAL CONFIG -->
  <template v-for="(_, key) in model" :key="key">
    <component
      v-model="model[key]"
      :is="generalConfigFormItems[key]"
      v-if="key in generalConfigFormItems"
    />
  </template>
</template>
