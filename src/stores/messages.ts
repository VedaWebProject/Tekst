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
  const info = (text: string) => text;
  const success = (text: string) => text;
  const warning = (text: string) => text;
  const error = (text: string) => text;
  const loading = (text: string) => text;

  return {
    info,
    success,
    warning,
    error,
    loading,
  };
});
