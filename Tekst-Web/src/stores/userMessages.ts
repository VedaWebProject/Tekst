import type {
  UserMessageCreate,
  UserMessageRead,
  UserMessageThread,
  UserRead,
  UserReadPublic,
} from '@/api';
import { DELETE, GET, POST } from '@/api';
import { useMessages } from '@/composables/messages';
import { $t } from '@/i18n';
import { useAuthStore } from '@/stores';
import { useIntervalFn } from '@vueuse/core';
import { defineStore } from 'pinia';
import { computed, ref } from 'vue';

export const useUserMessagesStore = defineStore('userMessages', () => {
  const auth = useAuthStore();
  const { message } = useMessages();

  const { pause: stopThreadsPolling, resume: startThreadsPolling } = useIntervalFn(
    async () => {
      if (auth.user) {
        await loadThreads();
      }
      if (unreadCount.value) {
        message.info($t('account.messages.msgUnreadCount', { count: unreadCount.value }));
      }
    },
    60 * 1000, // 1 minute
    { immediate: false, immediateCallback: true }
  );

  const threads = ref<UserMessageThread[]>([]);
  const loading = ref(false);
  const openThread = ref<UserMessageThread>();
  const showMessagingModal = ref(false);
  const preparedMsgContent = ref<string>();

  const unreadCount = computed<number>(() =>
    threads.value.map((t) => t.unread).reduce((a, b) => a + b, 0)
  );

  async function loadThreads() {
    loading.value = true;
    if (auth.user?.id) {
      const { data, error } = await GET('/messages/threads');
      if (!error) {
        // sort and apply threads data
        threads.value = data.sort((a, b) => {
          // sort by unread count, then by contact username
          const unreadDiff = b.unread - a.unread;
          if (unreadDiff !== 0) return unreadDiff;
          return (a.contact?.username || '').localeCompare(b.contact?.username || '');
        });
      } else {
        threads.value = [];
      }
    } else {
      threads.value = [];
    }
    loading.value = false;
  }

  async function loadMessages(
    threadId: string | null | undefined = openThread.value?.id
  ): Promise<UserMessageRead[] | undefined> {
    threadId = threadId || null;
    loading.value = true;
    if (auth.user?.id) {
      const { data, error } = await GET('/messages', {
        params: { query: { thread: threadId } },
      });
      loading.value = false;
      if (!error) {
        const thread = threads.value.find((t) => t.id === threadId);
        if (thread) {
          thread.unread = 0;
        }
        return data;
      }
    }
    loading.value = false;
    return undefined;
  }

  async function send(msg: UserMessageCreate) {
    loading.value = true;
    const { data, error } = await POST('/messages', {
      body: msg,
    });
    loading.value = false;
    if (!error) {
      return data;
    } else {
      return null;
    }
  }

  async function deleteThread(id: string) {
    loading.value = true;
    const { error } = await DELETE('/messages/threads/{id}', {
      params: { path: { id } },
    });
    if (!error) {
      threads.value = threads.value.filter((t) => (id === 'system' ? !!t.id : t.id !== id));
      message.success($t('account.messages.deleteThreadSuccess'));
    }
    loading.value = false;
  }

  function openConversation(withUser: UserRead | UserReadPublic, msgContent?: string) {
    preparedMsgContent.value = msgContent;
    const thread: UserMessageThread = threads.value.find(
      (t) => withUser && t.id === withUser.id
    ) || {
      id: withUser.id,
      contact: withUser,
      unread: 0,
    };
    openThread.value = thread;
    showMessagingModal.value = true;
  }

  return {
    threads,
    openThread,
    loading,
    unreadCount,
    showMessagingModal,
    preparedMsgContent,
    openConversation,
    loadThreads,
    loadMessages,
    send,
    deleteThread,
    startThreadsPolling,
    stopThreadsPolling,
  };
});
