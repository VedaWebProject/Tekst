<script setup lang="ts">
const props = defineProps<{
  layerTitle?: string;
}>();
</script>

<template>
  <div class="content-block">
    <h3>{{ props.layerTitle }}</h3>
    <slot></slot>
  </div>
</template>
