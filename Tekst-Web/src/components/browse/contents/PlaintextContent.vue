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
  <p v-for="content in resource.contents" :key="content.id" style="white-space: pre-wrap">
    <template v-if="content.text">
      <template v-if="!reduced">
        {{ content.text }}
      </template>
      <template v-else>
        {{ content.text.replace(/\n+/g, ' ') }}
      </template>
    </template>
  </p>
</template>
