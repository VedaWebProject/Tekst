import { defineStore } from 'pinia';

export interface Message {
  type?: 'info' | 'success' | 'warning' | 'error' | 'loading';
  text: string;
}

export const useMessagesStore = defineStore('messages', () => {
  /**
   * These store actions don't really do anything by themselves, but they can be
   * subscribed to via $onAction
   * (https://pinia.vuejs.org/core-concepts/actions.html#subscribing-to-actions).
   * See GlobalMessenger.vue, where this is used to pick up and dispatch messages.
   */
  const messageFn = (text: string, duration?: number) => ({ text, duration });
  const info = messageFn;
  const success = messageFn;
  const warning = messageFn;
  const error = messageFn;
  const loading = messageFn;

  return {
    info,
    success,
    warning,
    error,
    loading,
  };
});
