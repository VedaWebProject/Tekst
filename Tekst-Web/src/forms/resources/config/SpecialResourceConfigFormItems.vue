<script setup lang="ts">
import type { AnyResourceConfig, AnyResourceRead } from '@/api';
import { specialConfigFormItems } from '@/forms/resources/config/mappings';

defineProps<{
  resource: AnyResourceRead;
}>();

const model = defineModel<AnyResourceConfig['special']>({ required: true });
</script>

<template>
  <template v-if="!!model">
    <template v-for="(_, key) in model" :key="key">
      <component
        v-if="key in specialConfigFormItems"
        v-model="model[key]"
        :is="specialConfigFormItems[key]"
        :resource="resource"
      />
    </template>
  </template>
</template>
