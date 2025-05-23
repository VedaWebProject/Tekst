import type { MessageType } from 'naive-ui';
import { ref } from 'vue';

export interface Message {
  text: string;
  details?: string;
  type: MessageType;
  seconds: number;
}

// this needs to be globally shared, so it's defined outside of the composable
const messageQueue = ref<Message[]>([]);

export function useMessages() {
  function messageFn(type: MessageType) {
    return (text: string, details?: string | object, seconds: number = 5) => {
      messageQueue.value = messageQueue.value.concat([
        {
          text,
          details: details
            ? JSON.stringify(details, null, 2)
            : undefined,
          type,
          seconds,
        },
      ]);
    };
  }

  const message = {
    info: messageFn('info'),
    success: messageFn('success'),
    warning: messageFn('warning'),
    error: messageFn('error'),
    loading: messageFn('loading'),
  };

  return {
    messageQueue,
    message,
  };
}
