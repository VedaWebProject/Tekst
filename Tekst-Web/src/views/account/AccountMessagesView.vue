<script setup lang="ts">
import { $t } from '@/i18n';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import {
  DeleteIcon,
  MarkChatReadIcon,
  MarkChatUnreadIcon,
  MesssageIcon,
  NoContentIcon,
  SendIcon,
} from '@/icons';
import { useUserMessages, type MessageThread } from '@/composables/userMessages';
import { ref } from 'vue';
import { POST, type UserMessageCreate } from '@/api';
import {
  NButton,
  NInput,
  NIcon,
  NTime,
  NBadge,
  NSpace,
  NList,
  NListItem,
  type InputInst,
} from 'naive-ui';
import { useAuthStore } from '@/stores';
import { usePlatformData } from '@/composables/platformData';
import UserDisplay from '@/components/user/UserDisplay.vue';
import GenericModal from '@/components/generic/GenericModal.vue';
import HugeLabelledIcon from '@/components/generic/HugeLabelledIcon.vue';

const auth = useAuthStore();
const { pfData } = usePlatformData();
const { userMessages, threads, loading, unreadCount, createUserMessage, deleteUserMessageThread } =
  useUserMessages();

const openThread = ref<MessageThread>();
const showModal = ref(false);
const messageInput = ref<string>();
const messageInputRef = ref<InputInst>();
const loadingSend = ref(false);

async function markThreadRead(threadId?: string) {
  if (!threadId) return;
  const { data: updatedUserMessages, error } = await POST('/messages/threads/{id}/read', {
    params: { path: { id: threadId } },
  });
  if (!error) {
    userMessages.value = updatedUserMessages;
  }
}

async function handleSendMessage(msg: UserMessageCreate) {
  loadingSend.value = true;
  await createUserMessage(msg);
  openThread.value = threads.value.find((t) => t.id === openThread.value?.id);
  messageInput.value = '';
  await scrollDownMessageContainer(300);
  loadingSend.value = false;
}

function handleModalEnter() {
  messageInputRef.value?.focus();
  scrollDownMessageContainer();
  markThreadRead(openThread.value?.id);
}

async function scrollDownMessageContainer(delayMs: number = 0) {
  await new Promise((resolve) => setTimeout(resolve, delayMs));
  const messageContainerElm = document.getElementsByClassName('messages-scroll-container')[0];
  if (messageContainerElm) {
    messageContainerElm.scroll({ top: messageContainerElm.scrollHeight, behavior: 'smooth' });
  }
}

async function handleDeleteThread(e: UIEvent, id: string) {
  e.preventDefault();
  e.stopPropagation();
  await deleteUserMessageThread(id);
}
</script>

<template>
  <icon-heading level="1" :icon="MesssageIcon">
    {{ $t('account.messages.heading') }}
    <help-button-widget help-key="accountMessagesView" />
  </icon-heading>

  <div class="text-small translucent">
    {{ $t('account.messages.msgUnreadCount', { count: unreadCount }) }}
  </div>

  <div class="content-block">
    <n-list
      v-if="threads.length"
      hoverable
      clickable
      style="background-color: transparent"
      :style="{ opacity: loading ? 0.5 : 1, 'pointer-events': loading ? 'none' : 'auto' }"
    >
      <n-list-item
        v-for="thread in threads"
        :key="thread.id"
        @click="
          () => {
            openThread = thread;
            showModal = true;
          }
        "
      >
        <n-space align="center">
          <n-badge :value="thread.unreadCount" :offset="[10, 0]">
            <user-display v-if="thread.contact" :user="thread.contact" :link="false" />
            <span v-else>{{ pfData?.settings.infoPlatformName || 'System' }}</span>
          </n-badge>
        </n-space>

        <template #suffix>
          <n-button
            secondary
            :title="$t('general.deleteAction')"
            @click="(e) => handleDeleteThread(e, thread.id)"
          >
            <template #icon>
              <n-icon :component="DeleteIcon" />
            </template>
          </n-button>
        </template>
      </n-list-item>
    </n-list>
    <huge-labelled-icon
      v-else
      :icon="NoContentIcon"
      :message="$t('account.messages.msgNoMessages')"
    />
  </div>

  <generic-modal
    id="message-thread-modal"
    v-model:show="showModal"
    width="wide"
    style="max-height: 93vh"
    content-style="overflow: hidden scroll; padding-bottom: 0"
    content-class="messages-scroll-container"
    @after-leave="openThread = undefined"
    @after-enter="handleModalEnter"
  >
    <template #header>
      <user-display :user="openThread?.contact" :link="false" size="large" />
    </template>

    <template #default>
      <div style="display: flex; flex-direction: column; gap: var(--layout-gap)">
        <div
          v-for="message in openThread?.messages"
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
        v-if="openThread?.contact"
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
              recipient: openThread?.contact.id,
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
#message-thread-modal .message-content {
  position: relative;
  white-space: pre-wrap;
  border-radius: 24px;
  width: 80%;
  padding: 1.2rem;
}

#message-thread-modal .message-content.from-me {
  margin-left: auto;
  border-bottom-right-radius: 0px;
  background-color: var(--accent-color-fade4);
}

#message-thread-modal .message-content.from-them {
  margin-right: auto;
  border-bottom-left-radius: 0px;
  background-color: var(--main-bg-color);
}

#message-thread-modal .message-content > .message-meta {
  position: absolute;
  bottom: 8px;
  right: 16px;
  font-size: var(--font-size-tiny);
  opacity: 0.75;
}
</style>
