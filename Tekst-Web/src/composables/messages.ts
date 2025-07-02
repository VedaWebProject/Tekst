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
      details =
        !!details && typeof details !== 'string' && !(details instanceof String)
          ? (JSON.stringify(details || '', null, 2) as string) || undefined
          : (details as string) || undefined;
      messageQueue.value = messageQueue.value.concat([
        {
          text,
          details,
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
