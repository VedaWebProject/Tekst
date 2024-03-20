import { computed, ref } from 'vue';
import { DELETE, GET, POST } from '@/api';
import type { UserMessageCreate, UserMessageRead, UserReadPublic } from '@/api';
import { useAuthStore } from '@/stores';
import { watchEffect } from 'vue';
import { useMessages } from './messages';
import { $t } from '@/i18n';
import { usePlatformData } from './platformData';

export interface MessageThread {
  id: string;
  contact?: UserReadPublic;
  contactLabel: string;
  messages: UserMessageRead[];
  unreadCount: number;
}

const userMessages = ref<UserMessageRead[]>([]);
const lastUserId = ref<string>();

export function useUserMessages() {
  const auth = useAuthStore();
  const { pfData } = usePlatformData();
  const { message } = useMessages();

  const loading = ref(false);

  const unreadCount = computed<number>(
    () => userMessages.value.filter((m) => (auth.user?.id || '–') === m.recipient && !m.read).length
  );

  const threads = computed<MessageThread[]>(() => {
    if (!auth.user?.id) return [];
    const result: MessageThread[] = [];
    for (const message of userMessages.value) {
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

  async function loadUserMessages() {
    loading.value = true;
    if (auth.user?.id) {
      const { data, error } = await GET('/messages');
      if (!error) {
        userMessages.value = data;
      } else {
        userMessages.value = [];
      }
    } else {
      userMessages.value = [];
    }
    loading.value = false;
  }

  async function createUserMessage(msg: UserMessageCreate) {
    loading.value = true;
    const { data, error } = await POST('/messages', {
      body: msg,
    });
    if (!error) {
      userMessages.value = data;
      message.success($t('account.messages.createSuccess'), undefined, 1);
    }
    loading.value = false;
  }

  async function deleteUserMessage(id: string) {
    loading.value = true;
    const { data, error } = await DELETE('/messages/{id}', {
      params: { path: { id } },
    });
    if (!error) {
      userMessages.value = data;
      message.success($t('account.messages.deleteSuccess'));
    } else {
      auth.logout();
    }
    loading.value = false;
  }

  async function deleteUserMessageThread(id: string) {
    loading.value = true;
    const { data, error } = await DELETE('/messages/threads/{id}', {
      params: { path: { id } },
    });
    if (!error) {
      userMessages.value = data;
      message.success($t('account.messages.deleteSuccess'));
    } else {
      auth.logout();
    }
    loading.value = false;
  }

  watchEffect(() => {
    if (auth.loggedIn && auth.user?.id !== lastUserId.value) {
      lastUserId.value = auth.user?.id;
      loadUserMessages();
    }
  });

  return {
    userMessages,
    threads,
    loading,
    unreadCount,
    loadUserMessages,
    createUserMessage,
    deleteUserMessage,
    deleteUserMessageThread,
  };
}
