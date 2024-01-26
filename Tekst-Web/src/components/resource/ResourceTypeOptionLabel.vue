<script setup lang="ts">
defineProps<{
  label: string;
  extra?: string;
}>();
</script>

<template>
  {{ label }}
  <span v-if="extra" style="opacity: 0.5"> ({{ extra.trim() }})</span>
</template>
