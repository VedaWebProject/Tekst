<script setup lang="ts">
import type { UserMessageThread, UserReadPublic } from '@/api';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import MessageThreadListItem from '@/components/userMessages/MessageThreadListItem.vue';
import { $t } from '@/i18n';
import { MessageIcon, NoContentIcon } from '@/icons';
import { useUserMessagesStore } from '@/stores';
import { NEmpty, NIcon, NList, NSpin } from 'naive-ui';
import { onMounted } from 'vue';

const userMessages = useUserMessagesStore();

function handleThreadClick(thread: UserMessageThread, altContact?: UserReadPublic) {
  userMessages.openThread = { ...thread, contact: altContact || thread.contact };
  userMessages.showMessagingModal = true;
}

onMounted(() => {
  userMessages.loadThreads();
});
</script>

<template>
  <icon-heading level="1" :icon="MessageIcon">
    {{ $t('account.messages.heading') }}
    <help-button-widget help-key="accountMessagesView" />
  </icon-heading>

  <div v-if="userMessages.threads.length" class="text-small translucent">
    {{ $t('account.messages.msgUnreadCount', { count: userMessages.unreadCount }) }}
  </div>

  <div v-if="userMessages.threads.length" class="content-block">
    <h2>{{ $t('account.messages.headingThreads') }}</h2>
    <n-list hoverable clickable style="background-color: transparent">
      <message-thread-list-item
        v-for="(thread, index) in userMessages.threads"
        :key="`thread-${index}-${thread.id}`"
        :thread="thread"
        :disable-delete="userMessages.loading"
        @delete-thread="(id) => userMessages.deleteThread(id)"
        @click="handleThreadClick(thread)"
      />
    </n-list>
  </div>

  <n-spin
    v-else-if="userMessages.loading"
    :description="$t('common.loading')"
    class="centered-spinner"
  />

  <n-empty v-else :description="$t('account.messages.msgNoMessages')">
    <template #icon>
      <n-icon :component="NoContentIcon" />
    </template>
  </n-empty>
</template>
