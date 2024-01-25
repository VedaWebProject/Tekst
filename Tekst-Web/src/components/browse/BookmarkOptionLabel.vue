<script setup lang="ts">
import { NButton, NIcon, NEllipsis } from 'naive-ui';
import { DeleteIcon } from '@/icons';
import type { BookmarkRead } from '@/api';

defineProps<{
  bookmark: BookmarkRead;
  levelLabel: string;
}>();

const emit = defineEmits(['delete']);

function handleDeleteClick(e: MouseEvent) {
  e.preventDefault();
  e.stopPropagation();
  emit('delete');
}
</script>

<template>
  <div>
    <div
      style="display: flex; justify-content: space-between; align-items: center; max-width: 90vw"
    >
      <n-ellipsis>{{ levelLabel }}: {{ bookmark.label }}</n-ellipsis>
      <n-button
        secondary
        size="small"
        :title="$t('general.deleteAction')"
        @click="handleDeleteClick"
      >
        <template #icon>
          <n-icon :component="DeleteIcon" />
        </template>
      </n-button>
    </div>
    <div>{{ bookmark.comment }}</div>
  </div>
</template>
