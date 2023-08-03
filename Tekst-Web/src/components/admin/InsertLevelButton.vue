<script setup lang="ts">
import { NButton, NIcon } from 'naive-ui';
import AddRound from '@vicons/material/AddRound';
import { useI18n } from 'vue-i18n';

defineProps<{
  level: number;
}>();
defineEmits(['click']);

const { t } = useI18n({ useScope: 'global' });
</script>

<template>
  <div class="add-level-wrapper">
    <div class="add-level-separator"></div>
    <n-button
      secondary
      circle
      :title="t('admin.texts.levels.tipInsertLevel', { n: level + 1 })"
      @click="$emit('click', level)"
      :focusable="false"
    >
      <template #icon>
        <n-icon :component="AddRound" />
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
