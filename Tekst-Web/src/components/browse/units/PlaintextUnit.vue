<script setup lang="ts">
import type { PlaintextLayerConfig } from '@/api';

defineProps<{
  layer: Record<string, any>;
  layerConfig: PlaintextLayerConfig;
}>();
</script>

<template>
  <div v-for="unit in layer.units" :key="unit.id" style="white-space: pre-wrap">
    {{ unit.text }}
  </div>
</template>
