<script setup lang="ts">
import { $t } from '@/i18n';
import { MarkChatReadIcon, MarkChatUnreadIcon, SendIcon } from '@/icons';
import { ref } from 'vue';
import { NButton, NInput, NIcon, NTime, type InputInst } from 'naive-ui';
import { useAuthStore, useUserMessagesStore } from '@/stores';
import UserDisplay from '@/components/user/UserDisplay.vue';
import GenericModal from '@/components/generic/GenericModal.vue';
import { useMagicKeys, whenever } from '@vueuse/core';
import type { UserMessageRead } from '@/api';

const userMessages = useUserMessagesStore();
const auth = useAuthStore();
const keys = useMagicKeys();
const ctrlEnter = keys['Ctrl+Enter'];

const messages = ref<UserMessageRead[]>();
const messageInput = ref<string>();
const messageInputRef = ref<InputInst>();
const loadingSend = ref(false);

async function handleSendMessage() {
  if (!messageInput.value || loadingSend.value) return;
  loadingSend.value = true;
  const msg = await userMessages.send({
    content: messageInput.value || '',
    sender: auth.user?.id,
    recipient: userMessages.openThread?.contact?.id || '',
  });
  msg && messages.value?.push(msg);
  messageInput.value = '';
  await scrollDownMessageContainer(300);
  loadingSend.value = false;
  messageInputRef.value?.focus();
}

async function handleModalEnter() {
  messageInputRef.value?.focus();
  messages.value = await userMessages.loadMessages(userMessages.openThread?.id);
  scrollDownMessageContainer();
}

function handleModalLeave() {
  userMessages.openThread = undefined;
  messages.value = undefined;
}

async function scrollDownMessageContainer(delayMs: number = 0) {
  await new Promise((resolve) => setTimeout(resolve, delayMs));
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
      <div
        v-if="!!messages?.length"
        style="display: flex; flex-direction: column; gap: var(--layout-gap)"
      >
        <div
          v-for="msg in messages"
          :key="msg.id"
          class="message-content"
          :class="{
            'from-me': msg.sender === auth.user?.id,
            'from-them': msg.sender !== auth.user?.id,
          }"
          style="white-space: pre-wrap"
        >
          {{ msg.content }}
          <div
            style="display: flex; align-items: center; gap: var(--content-gap)"
            class="message-meta"
          >
            <n-time :time="new Date(msg.time || '')" type="datetime" />
            <n-icon
              v-if="msg.sender === auth.user?.id"
              :component="msg.read ? MarkChatReadIcon : MarkChatUnreadIcon"
              :title="$t(msg.read ? 'account.messages.read' : 'account.messages.unread')"
              :color="msg.read ? 'var(--col-success)' : 'inherit'"
            />
          </div>
        </div>
      </div>
    </template>

    <template #footer>
      <div
        v-if="userMessages.openThread?.contact"
        style="
          display: flex;
          gap: var(--layout-gap);
          align-items: end;
          padding-top: var(--layout-gap);
        "
      >
        <n-input
          ref="messageInputRef"
          v-model:value="messageInput"
          type="textarea"
          :placeholder="$t('account.messages.message')"
          :resizable="false"
          :autosize="{ minRows: 1, maxRows: 3 }"
          show-count
          :maxlength="1000"
          :allow-input="(v) => v.length == 0 || v.replace(/[\s\n\t]+/g, '').length > 0"
          style="flex-grow: 2"
        />
        <n-button
          type="primary"
          :title="$t('account.messages.btnSend')"
          :loading="loadingSend"
          :disabled="loadingSend || !messageInput || messageInput.length < 1"
          @click="handleSendMessage"
        >
          <template #icon>
            <n-icon :component="SendIcon" />
          </template>
        </n-button>
      </div>
    </template>
  </generic-modal>
</template>

<style>
#messaging-modal .message-content {
  position: relative;
  white-space: pre-wrap;
  border-radius: 24px;
  width: 80%;
  padding: 1.2rem;
}

#messaging-modal .message-content.from-me {
  margin-left: auto;
  border-bottom-right-radius: 0px;
  background-color: var(--accent-color-fade4);
}

#messaging-modal .message-content.from-them {
  margin-right: auto;
  border-bottom-left-radius: 0px;
  background-color: var(--main-bg-color);
}

#messaging-modal .message-content > .message-meta {
  position: absolute;
  bottom: 8px;
  right: 16px;
  font-size: var(--font-size-tiny);
  opacity: 0.75;
}
</style>
