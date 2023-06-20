<script setup lang="ts">
import type { PlainTextLayerConfig } from '@/openapi';

const props = defineProps<{
  layer: Record<string, any>;
  layerConfig: PlainTextLayerConfig;
}>();
</script>

<template>
  <div style="white-space: pre-wrap">
    {{ props.layer.unit.text }}
  </div>
</template>
