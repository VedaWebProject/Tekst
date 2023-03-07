<script setup lang="ts">
const props = defineProps<{
  title: string;
  subtitle?: string;
  accentColor?: string;
}>();
</script>

<template>
  <div class="text-select-option" :title="props.subtitle">
    <div class="text-select-option-indicator" :style="{ backgroundColor: props.accentColor }"></div>
    <div class="text-select-option-label">
      {{ props.title }}
    </div>
  </div>
</template>

<style scoped>
.text-select-option {
  display: flex;
  align-items: center;
  gap: 12px;
}

.text-select-option-indicator {
  width: 20px;
  height: 20px;
  border-radius: 50%;
}

.n-dropdown-option-body--disabled .text-select-option-indicator {
  background-color: #777 !important /* has to override inline style */;
}
</style>
