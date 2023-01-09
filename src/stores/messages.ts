import { defineStore } from 'pinia';

export interface Message {
  type?: 'default' | 'info' | 'success' | 'warning' | 'error' | 'loading';
  text: string;
}

export const useMessagesStore = defineStore('messages', () => {
  // const queue = ref<Message[]>([]);

  /**
   * This store action doesn't really do anything by itself, but it can be
   * subscribed to via $onAction
   * (https://pinia.vuejs.org/core-concepts/actions.html#subscribing-to-actions).
   * See GlobalMessenger.vue, where this is used to react to messages.
   */
  function create(msg: Message) {
    // queue.value.push(msg);
    return msg;
  }

  return {
    // queue,
    create,
  };
});
