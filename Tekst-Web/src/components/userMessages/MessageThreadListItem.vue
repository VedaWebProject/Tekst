<script setup lang="ts">
import type { UserMessageThread } from '@/api';
import { DeleteIcon } from '@/icons';
import { NListItem, NFlex, NBadge, NButton, NIcon } from 'naive-ui';
import UserDisplay from '@/components/user/UserDisplay.vue';

const props = defineProps<{
  thread: UserMessageThread;
  disableDelete?: boolean;
}>();

const emits = defineEmits(['deleteThread']);

function handleDeleteClick(e: UIEvent) {
  e.stopPropagation();
  e.preventDefault();
  emits('deleteThread', props.thread.id || 'system');
}
</script>

<template>
  <n-list-item>
    <n-flex align="center">
      <n-badge :value="thread.unread" :offset="[10, 0]">
        <user-display v-if="thread.contact" :user="thread.contact" :link="false" />
        <span v-else>???</span>
      </n-badge>
    </n-flex>

    <template #suffix>
      <n-button
        secondary
        :title="$t('account.messages.deleteThread')"
        :disabled="disableDelete"
        @click="handleDeleteClick"
      >
        <template #icon>
          <n-icon :component="DeleteIcon" />
        </template>
      </n-button>
    </template>
  </n-list-item>
</template>
