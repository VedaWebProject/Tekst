<script setup lang="ts">
import type { PlainTextLayerConfig, PlainTextUnitRead } from '@/openapi';

const props = defineProps<{
  unitData: PlainTextUnitRead;
  layerConfig: PlainTextLayerConfig;
}>();
</script>

<template>
  <div style="white-space: pre-wrap">
    {{ props.unitData.text }}
  </div>
</template>
