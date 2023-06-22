<script setup lang="ts">
import type { PlainTextLayerConfig } from '@/openapi';

defineProps<{
  layer: Record<string, any>;
  layerConfig: PlainTextLayerConfig;
}>();
</script>

<template>
  <div v-for="unit in layer.units" :key="unit.id" style="white-space: pre-wrap">
    {{ unit.text }}
  </div>
</template>
