<script setup lang="ts">
const props = defineProps<{ data: Record<string, any> }>();
</script>

<template>
  <div>{{ props.data.text }}</div>
</template>
