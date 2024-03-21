<script setup lang="ts">
import { $t } from '@/i18n';
import { MarkChatReadIcon, MarkChatUnreadIcon, SendIcon } from '@/icons';
import { ref } from 'vue';
import { POST, type UserMessageCreate } from '@/api';
import { NButton, NInput, NIcon, NTime, type InputInst } from 'naive-ui';
import { useAuthStore, useUserMessagesStore } from '@/stores';
import UserDisplay from '@/components/user/UserDisplay.vue';
import GenericModal from '@/components/generic/GenericModal.vue';

const userMessages = useUserMessagesStore();
const auth = useAuthStore();

const messageInput = ref<string>();
const messageInputRef = ref<InputInst>();
const loadingSend = ref(false);

async function markThreadRead(threadId?: string) {
  if (!threadId) return;
  const { data: updatedUserMessages, error } = await POST('/messages/threads/{id}/read', {
    params: { path: { id: threadId } },
  });
  if (!error) {
    userMessages.messages = updatedUserMessages;
  }
}

async function handleSendMessage(msg: UserMessageCreate) {
  loadingSend.value = true;
  await userMessages.send(msg);
  userMessages.openThread = userMessages.threads.find((t) => t.id === userMessages.openThread?.id);
  messageInput.value = '';
  await scrollDownMessageContainer(300);
  loadingSend.value = false;
}

function handleModalEnter() {
  messageInputRef.value?.focus();
  scrollDownMessageContainer();
  markThreadRead(userMessages.openThread?.id);
}

async function scrollDownMessageContainer(delayMs: number = 0) {
  await new Promise((resolve) => setTimeout(resolve, delayMs));
  const messageContainerElm = document.getElementsByClassName('messages-scroll-container')[0];
  if (messageContainerElm) {
    messageContainerElm.scroll({ top: messageContainerElm.scrollHeight, behavior: 'smooth' });
  }
}
</script>

<template>
  <generic-modal
    id="messaging-modal"
    v-model:show="userMessages.showMessagingModal"
    width="wide"
    style="max-height: 93vh"
    content-style="overflow: hidden scroll; padding-bottom: 0"
    content-class="messages-scroll-container"
    @after-leave="userMessages.openThread = undefined"
    @after-enter="handleModalEnter"
  >
    <template #header>
      <user-display :user="userMessages.openThread?.contact" :link="false" size="large" />
    </template>

    <template #default>
      <div style="display: flex; flex-direction: column; gap: var(--layout-gap)">
        <div
          v-for="message in userMessages.openThread?.messages"
          :key="message.id"
          class="message-content"
          :class="{
            'from-me': message.sender === auth.user?.id,
            'from-them': message.sender !== auth.user?.id,
          }"
          style="white-space: pre-wrap"
        >
          {{ message.content }}
          <div
            style="display: flex; align-items: center; gap: var(--content-gap)"
            class="message-meta"
          >
            <n-time :time="new Date(message.time || '')" type="datetime" />
            <n-icon
              v-if="message.sender === auth.user?.id"
              :component="message.read ? MarkChatReadIcon : MarkChatUnreadIcon"
              :title="$t(message.read ? 'account.messages.read' : 'account.messages.unread')"
              :color="message.read ? 'var(--col-success)' : 'inherit'"
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
          style="flex-grow: 2"
          :placeholder="$t('account.messages.inputPlaceholder')"
          :resizable="false"
          :autosize="{ minRows: 1, maxRows: 3 }"
          show-count
          :minlength="1"
          :maxlength="1000"
          :disabled="loadingSend"
        />
        <n-button
          type="primary"
          :title="$t('account.messages.btnSend')"
          :loading="loadingSend"
          :disabled="loadingSend || !messageInput || messageInput.length <= 1"
          @click="
            handleSendMessage({
              content: messageInput || '',
              sender: auth.user?.id,
              recipient: userMessages.openThread?.contact.id,
            })
          "
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
