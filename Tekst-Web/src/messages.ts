import type { MessageType } from 'naive-ui';
import { ref } from 'vue';

interface Message {
  text: string;
  type: MessageType;
  durationSeconds: number;
}

// this needs to be globally shared, so it's defined outside of the composable
const messageQueue = ref<Message[]>([]);

export function useMessages() {
  function messageFn(type: MessageType) {
    return (text: string, durationSeconds: number = 5) => {
      messageQueue.value = messageQueue.value.concat([
        {
          text,
          type,
          durationSeconds,
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
