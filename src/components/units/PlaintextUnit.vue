<script setup lang="ts">
const props = defineProps<{ data: Record<string, any> }>();
</script>

<template>
  <div style="white-space: pre-wrap">
    {{ props.data.text }}
  </div>
</template>
