<script setup lang="ts">
import { NButton, NIcon } from 'naive-ui';

import { AddIcon } from '@/icons';

defineProps<{
  title?: string;
  disabled?: boolean;
}>();
defineEmits(['click']);
</script>

<template>
  <div class="add-level-wrapper">
    <div class="add-level-separator"></div>
    <n-button
      secondary
      circle
      size="small"
      :title="title"
      :disabled="disabled"
      :focusable="false"
      @click="$emit('click')"
    >
      <template #icon>
        <n-icon :component="AddIcon" />
      </template>
    </n-button>
    <div class="add-level-separator"></div>
  </div>
</template>

<style scoped>
.add-level-wrapper {
  display: flex;
  align-items: center;
  padding: 6px 0;
  text-align: center;
}

.add-level-separator {
  flex-grow: 2;
  height: 0;
  border-bottom: 1px dashed #888;
  opacity: 0.25;
}
</style>
