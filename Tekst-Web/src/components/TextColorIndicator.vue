<script setup lang="ts">
defineProps<{ noBorder?: boolean }>();
</script>

<template>
  <div
    class="text-color-indicator"
    :style="{ border: noBorder ? 'none' : '1px solid var(--base-color-translucent)' }"
  ></div>
</template>

<style scoped>
.text-color-indicator {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background-color: var(--working-text-color);
}
</style>
