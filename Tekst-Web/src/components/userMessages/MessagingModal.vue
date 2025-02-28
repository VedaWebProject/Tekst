<script setup lang="ts">
import type { UserMessageRead } from '@/api';
import GenericModal from '@/components/generic/GenericModal.vue';
import UserDisplay from '@/components/user/UserDisplay.vue';
import { $t } from '@/i18n';
import { MarkChatReadIcon, MarkChatUnreadIcon, SendIcon } from '@/icons';
import { useAuthStore, useUserMessagesStore } from '@/stores';
import { delay, utcToLocalTime } from '@/utils';
import { useIntervalFn, useMagicKeys, whenever } from '@vueuse/core';
import { NButton, NFlex, NIcon, NInput, NTime, useThemeVars, type InputInst } from 'naive-ui';
import { ref } from 'vue';

const userMessages = useUserMessagesStore();
const auth = useAuthStore();
const nuiTheme = useThemeVars();
const keys = useMagicKeys();
const ctrlEnter = keys['Ctrl+Enter'];

const messages = ref<UserMessageRead[]>();
const messageInput = ref<string>();
const messageInputRef = ref<InputInst>();
const loadingSend = ref(false);

const { pause: stopMessagesPolling, resume: startMessagesPolling } = useIntervalFn(
  async () => {
    const loadedMessages = await userMessages.loadMessages();
    if (loadedMessages?.length && loadedMessages.length !== messages.value?.length) {
      messages.value = loadedMessages;
    }
  },
  10 * 1000, // 10 seconds
  { immediate: false, immediateCallback: true }
);

async function handleSendMessage() {
  if (!messageInput.value || loadingSend.value) return;
  loadingSend.value = true;
  const msg = await userMessages.send({
    content: messageInput.value || '',
    sender: auth.user?.id,
    recipient: userMessages.openThread?.contact?.id || '',
  });
  if (msg) messages.value?.push(msg);
  messageInput.value = '';
  await scrollDownMessageContainer(300);
  loadingSend.value = false;
  messageInputRef.value?.focus();
}

async function handleModalEnter() {
  messageInput.value = userMessages.preparedMsgContent;
  userMessages.preparedMsgContent = undefined;
  messageInputRef.value?.focus();
  startMessagesPolling();
  await scrollDownMessageContainer(300);
}

function handleModalLeave() {
  stopMessagesPolling();
  userMessages.openThread = undefined;
  messages.value = undefined;
}

async function scrollDownMessageContainer(delayMs: number = 0) {
  await delay(delayMs);
  const messageContainerElm = document.getElementsByClassName('messages-scroll-container')[0];
  if (messageContainerElm) {
    messageContainerElm.scroll({ top: messageContainerElm.scrollHeight, behavior: 'smooth' });
  }
}

whenever(ctrlEnter, () => {
  handleSendMessage();
});
</script>

<template>
  <generic-modal
    id="messaging-modal"
    v-model:show="userMessages.showMessagingModal"
    width="wide"
    style="max-height: 93vh"
    content-style="overflow: hidden scroll; padding-bottom: 0"
    content-class="messages-scroll-container"
    @after-leave="handleModalLeave"
    @after-enter="handleModalEnter"
  >
    <template #header>
      <user-display
        :user="userMessages.openThread?.contact || undefined"
        :link="false"
        size="large"
      />
    </template>

    <template #default>
      <n-flex v-if="!!messages?.length" vertical size="large">
        <div
          v-for="msg in messages"
          :key="msg.id"
          class="message-bubble"
          :class="{
            'from-me': msg.sender === auth.user?.id,
            'from-them': msg.sender !== auth.user?.id,
          }"
        >
          <div class="text-medium pre-wrap">{{ msg.content }}</div>
          <n-flex align="center" class="message-meta">
            <n-time v-if="msg.createdAt" :time="utcToLocalTime(msg.createdAt)" type="datetime" />
            <n-icon
              v-if="msg.sender === auth.user?.id"
              :component="msg.read ? MarkChatReadIcon : MarkChatUnreadIcon"
              :title="$t(msg.read ? 'account.messages.read' : 'account.messages.unread')"
              :color="msg.read ? nuiTheme.successColor : 'inherit'"
            />
          </n-flex>
        </div>
      </n-flex>
    </template>

    <template #footer>
      <n-flex class="mt-lg" :wrap="false">
        <n-input
          ref="messageInputRef"
          v-model:value="messageInput"
          type="textarea"
          :placeholder="$t('account.messages.message')"
          :resizable="false"
          :autosize="{ minRows: 1, maxRows: 3 }"
          show-count
          :maxlength="1000"
          :disabled="!userMessages.openThread?.id"
          :allow-input="(v) => v.length == 0 || v.replace(/[\s\n\t]+/g, '').length > 0"
          style="flex-grow: 2"
        />
        <n-button
          type="primary"
          :title="`${$t('account.messages.btnSend')} (${$t('general.ctrlEnter')})`"
          :loading="loadingSend"
          :disabled="
            loadingSend || !messageInput || messageInput.length < 1 || !userMessages.openThread?.id
          "
          @click="handleSendMessage"
        >
          <template #icon>
            <n-icon :component="SendIcon" />
          </template>
        </n-button>
      </n-flex>
      <div class="messaging-status text-tiny translucent mt-md">
        <template v-if="messages?.length == null">
          {{ $t('general.loading') }}
        </template>
        <template v-else>
          {{ $t('account.messages.msgCount', { count: messages?.length || 0 }) }}
        </template>
      </div>
    </template>
  </generic-modal>
</template>

<style>
#messaging-modal .message-bubble {
  position: relative;
  border-radius: 24px;
  width: 80%;
  padding: 1.2rem;
}

#messaging-modal .message-bubble.from-me {
  margin-left: auto;
  border-bottom-right-radius: 0px;
  background-color: var(--accent-color-fade4);
}

#messaging-modal .message-bubble.from-them {
  margin-right: auto;
  border-bottom-left-radius: 0px;
  background-color: var(--main-bg-color);
}

#messaging-modal .message-bubble > .message-meta {
  position: absolute;
  bottom: 8px;
  right: 16px;
  font-size: var(--font-size-tiny);
  opacity: 0.75;
}

#messaging-modal .message-bubble q {
  font-style: italic;
  opacity: 0.75;
}

#messaging-modal .message-bubble q::before {
  content: '\00BB';
  font-weight: var(--font-weight-bold);
  font-size: var(--font-size-huge);
  margin-right: var(--gap-sm);
  color: var(--accent-color);
  line-height: 1;
}

#messaging-modal .messaging-status {
  text-align: center;
}
</style>
