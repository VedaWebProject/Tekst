<script setup lang="ts">
import type { AnyResourceRead } from '@/api';

withDefaults(
  defineProps<{
    resource: AnyResourceRead;
    reduced?: boolean;
  }>(),
  {
    reduced: false,
  }
);
</script>

<template>
  <div v-for="unit in resource.units" :key="unit.id" style="white-space: pre-wrap">
    {{ unit.text }}
  </div>
</template>
