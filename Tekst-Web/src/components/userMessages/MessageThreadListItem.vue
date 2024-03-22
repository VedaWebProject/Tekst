<script setup lang="ts">
import { DeleteIcon } from '@/icons';
import type { UserMessageThread } from '@/stores';
import { NListItem, NSpace, NBadge, NButton, NIcon } from 'naive-ui';

const props = defineProps<{
  thread: UserMessageThread;
  platformName?: string;
}>();

const emits = defineEmits(['deleteThread']);

function handleDeleteClick(e: UIEvent) {
  e.stopPropagation();
  e.preventDefault();
  emits('deleteThread', props.thread.id);
}
</script>

<template>
  <n-list-item>
    <n-space align="center">
      <n-badge :value="thread.unreadCount" :offset="[10, 0]">
        <user-display v-if="thread.contact" :user="thread.contact" :link="false" />
        <span v-else>{{ platformName || 'System' }}</span>
      </n-badge>
    </n-space>

    <template #suffix>
      <n-button secondary :title="$t('general.deleteAction')" @click="handleDeleteClick">
        <template #icon>
          <n-icon :component="DeleteIcon" />
        </template>
      </n-button>
    </template>
  </n-list-item>
</template>
