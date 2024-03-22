<script setup lang="ts">
import { $t } from '@/i18n';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import { MessageIcon, NoContentIcon } from '@/icons';
import { NList } from 'naive-ui';
import { useUserMessagesStore, type UserMessageThread } from '@/stores';
import { usePlatformData } from '@/composables/platformData';
import HugeLabelledIcon from '@/components/generic/HugeLabelledIcon.vue';
import MessageThreadListItem from '@/components/userMessages/MessageThreadListItem.vue';

const { pfData } = usePlatformData();
const userMessages = useUserMessagesStore();

function handleThreadClick(thread: UserMessageThread) {
  userMessages.openThread = thread;
  userMessages.showMessagingModal = true;
}
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
    <n-list
      hoverable
      clickable
      style="background-color: transparent"
      :style="{
        opacity: userMessages.loading ? 0.5 : 1,
        'pointer-events': userMessages.loading ? 'none' : 'auto',
      }"
    >
      <message-thread-list-item
        v-for="thread in userMessages.threads"
        :key="thread.id"
        :thread="thread"
        :platform-name="pfData?.settings.infoPlatformName"
        @delete-thread="(id) => userMessages.deleteThread(id)"
        @click="handleThreadClick(thread)"
      />
    </n-list>
  </div>

  <huge-labelled-icon
    v-else
    :icon="NoContentIcon"
    :message="$t('account.messages.msgNoMessages')"
  />
</template>
