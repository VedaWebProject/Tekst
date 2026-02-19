<script setup lang="ts">
import type { UserMessageThread } from '@/api';
import UserDisplay from '@/components/user/UserDisplay.vue';
import { $t } from '@/i18n';
import { DeleteIcon } from '@/icons';
import { renderIcon } from '@/utils';
import { NBadge, NButton, NFlex, NIcon, NListItem, useDialog } from 'naive-ui';

const props = defineProps<{
  thread: UserMessageThread;
  disableDelete?: boolean;
}>();

const emits = defineEmits(['deleteThread']);
const dialog = useDialog();

function handleDeleteClick() {
  dialog.create({
    title: $t('common.delete'),
    icon: renderIcon(DeleteIcon),
    content: $t('common.areYouSure'),
    positiveText: $t('common.yes'),
    negativeText: $t('common.no'),
    onPositiveClick: () => emits('deleteThread', props.thread.id || 'system'),
  });
}
</script>

<template>
  <n-list-item>
    <n-flex align="center">
      <n-badge :value="thread.unread" :offset="[10, 0]">
        <user-display
          :user="
            !thread.contact || thread.contact.username === 'system' ? undefined : thread.contact
          "
          :link="false"
          :system="!thread.contact || thread.contact.username === 'system'"
        />
      </n-badge>
    </n-flex>

    <template #suffix>
      <n-button
        secondary
        :title="$t('account.messages.deleteThread')"
        :disabled="disableDelete"
        @click.stop.prevent="handleDeleteClick"
      >
        <template #icon>
          <n-icon :component="DeleteIcon" />
        </template>
      </n-button>
    </template>
  </n-list-item>
</template>
