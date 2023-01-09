import { ref, type Ref } from 'vue';
import { defineStore } from 'pinia';

export interface Message {
  type: 'info' | 'success' | 'warning' | 'error' | 'loading';
  text: string;
}

export const useMessagesStore = defineStore('messages', () => {
  const queue: Ref<Message[]> = ref([]);
  function create(text: Message['text'], type: Message['type']) {
    queue.value.push({ text, type });
  }
  return {
    queue,
    create,
  };
});
