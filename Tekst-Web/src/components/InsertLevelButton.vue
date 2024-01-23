<script setup lang="ts">
import { NButton, NIcon } from 'naive-ui';

import { AddIcon } from '@/icons';

defineProps<{
  level: number;
}>();
defineEmits(['click']);
</script>

<template>
  <div class="add-level-wrapper">
    <div class="add-level-separator"></div>
    <n-button
      secondary
      circle
      :title="$t('admin.text.levels.tipInsertLevel', { n: level + 1 })"
      :focusable="false"
      @click="$emit('click', level)"
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
