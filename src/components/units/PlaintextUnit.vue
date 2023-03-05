<script setup lang="ts">
import type { PlainTextUnitRead } from '@/openapi';
import UnitContainer from './UnitContainer.vue';
const props = defineProps<PlainTextUnitRead>();
</script>

<template>
  <UnitContainer :layer-title="props.layerId">
    <div>{{ props.text }}</div>
  </UnitContainer>
</template>
