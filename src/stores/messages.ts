import { ref } from 'vue';
import { defineStore } from 'pinia';

export interface Message {
  type?: 'default' | 'info' | 'success' | 'warning' | 'error' | 'loading';
  text: string;
}

export const useMessagesStore = defineStore('messages', () => {
  const queue = ref<Message[]>([]);

  function create(msg: Message) {
    queue.value.push(msg);
  }

  return {
    queue,
    create,
  };
});
