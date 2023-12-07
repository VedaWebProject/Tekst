<script setup lang="ts">
import type { AnyLayerRead } from '@/api';

withDefaults(
  defineProps<{
    layer: AnyLayerRead;
    reduced?: boolean;
  }>(),
  {
    reduced: false,
  }
);
</script>

<template>
  <div v-for="unit in layer.units" :key="unit.id" style="white-space: pre-wrap">
    {{ unit.text }}
  </div>
</template>
