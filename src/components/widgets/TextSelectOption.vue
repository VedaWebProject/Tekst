<script setup lang="ts">
import type { TextRead } from '@/openapi';

defineProps<{
  text: TextRead;
  selected?: boolean;
}>();
</script>

<template>
  <div class="text-select-option" :title="text.subtitle">
    <div class="text-select-option-indicator" :style="{ backgroundColor: text.accentColor }"></div>
    <div class="text-select-option-label">
      {{ text.title }}
      {{ !text.isActive ? `[${$t('models.text.isInactive')}]` : '' }}
      {{ !!selected ? `(${$t('general.selected')})` : '' }}
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
  background-color: #bbb !important /* has to override inline style */;
}
</style>
