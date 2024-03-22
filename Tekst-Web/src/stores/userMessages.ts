import { computed, ref } from 'vue';
import { DELETE, GET, POST } from '@/api';
import type { UserMessageCreate, UserMessageRead, UserReadPublic } from '@/api';
import { useAuthStore } from '@/stores';
import { watchEffect } from 'vue';
import { useMessages } from '@/composables/messages';
import { $t } from '@/i18n';
import { usePlatformData } from '@/composables/platformData';
import { defineStore } from 'pinia';

export interface UserMessageThread {
  id: string;
  contact?: UserReadPublic;
  contactLabel: string;
  messages: UserMessageRead[];
  unreadCount: number;
}

export const useUserMessagesStore = defineStore('userMessages', () => {
  const auth = useAuthStore();
  const { pfData } = usePlatformData();
  const { message } = useMessages();

  const messages = ref<UserMessageRead[]>([]);
  const lastUserId = ref<string>();
  const loading = ref(false);
  const openThread = ref<UserMessageThread>();
  const showMessagingModal = ref(false);

  const unreadCount = computed<number>(
    () => messages.value.filter((m) => (auth.user?.id || '–') === m.recipient && !m.read).length
  );

  const threads = computed<UserMessageThread[]>(() => {
    if (!auth.user?.id) return [];
    const result: UserMessageThread[] = [];
    for (const message of messages.value) {
      const contact: UserReadPublic | undefined =
        (message.recipientUser.id !== auth.user.id ? message.recipientUser : message.senderUser) ||
        undefined;
      const threadId = contact?.id || 'system';
      const thread = result.find((t) => t.id === threadId);
      if (!thread) {
        result.push({
          id: threadId,
          contact,
          contactLabel:
            contact?.name ||
            contact?.username ||
            pfData.value?.settings.infoPlatformName ||
            'System',
          messages: [message],
          unreadCount: auth.user.id === message.recipient && !message.read ? 1 : 0,
        });
      } else {
        thread.messages.push(message);
        if (auth.user.id === message.recipient && !message.read) thread.unreadCount++;
      }
    }
    // sort messages in threads by time
    for (const thread of result) {
      thread.messages.sort(
        (a, b) => new Date(a.time || '').getTime() - new Date(b.time || '').getTime()
      );
    }
    // sort threads by most current message
    result.sort(
      (a, b) =>
        new Date(a.messages[0].time || '').getTime() - new Date(b.messages[0].time || '').getTime()
    );
    return result;
  });

  async function load() {
    loading.value = true;
    if (auth.user?.id) {
      const { data, error } = await GET('/messages');
      if (!error) {
        messages.value = data;
      } else {
        messages.value = [];
      }
    } else {
      messages.value = [];
    }
    loading.value = false;
  }

  async function send(msg: UserMessageCreate) {
    loading.value = true;
    const { data, error } = await POST('/messages', {
      body: msg,
    });
    if (!error) {
      messages.value = data;
      message.success($t('account.messages.createSuccess'), undefined, 1);
    }
    loading.value = false;
  }

  async function deleteMessage(id: string) {
    loading.value = true;
    const { data, error } = await DELETE('/messages/{id}', {
      params: { path: { id } },
    });
    if (!error) {
      messages.value = data;
      message.success($t('account.messages.deleteSuccess'));
    } else {
      auth.logout();
    }
    loading.value = false;
  }

  async function deleteThread(id: string) {
    loading.value = true;
    const { data, error } = await DELETE('/messages/threads/{id}', {
      params: { path: { id } },
    });
    if (!error) {
      messages.value = data;
      message.success($t('account.messages.deleteSuccess'));
    } else {
      auth.logout();
    }
    loading.value = false;
  }

  watchEffect(() => {
    if (auth.loggedIn && auth.user?.id !== lastUserId.value) {
      lastUserId.value = auth.user?.id;
      load();
    }
  });

  return {
    messages,
    threads,
    openThread,
    loading,
    unreadCount,
    showMessagingModal,
    load,
    send,
    deleteMessage,
    deleteThread,
  };
});
