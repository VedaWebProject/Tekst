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
  <p v-for="unit in resource.units" :key="unit.id" style="white-space: pre-wrap">
    <template v-if="unit.text">
      <template v-if="!reduced">
        {{ unit.text }}
      </template>
      <template v-else>
        {{ unit.text.replace(/\n+/g, ' ') }}
      </template>
    </template>
  </p>
</template>
