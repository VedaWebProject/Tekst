<script setup lang="ts">
import GlobalMessage from '@/components/messages/GlobalMessage.vue';
import GlobalMessageContent from '@/components/messages/GlobalMessageContent.vue';
import { useMessages } from '@/composables/messages';
import { NMessageProvider, useMessage, type MessageRenderMessage } from 'naive-ui';
import type { RenderMessageProps } from 'naive-ui/es/message/src/types';
import { defineComponent, h, watch } from 'vue';

const renderMessage: MessageRenderMessage = (props: RenderMessageProps) => {
  return h(
    GlobalMessage,
    {
      type: props.type,
      closable: props.closable,
      onClose: props.onClose,
    },
    {
      default: props.content,
    }
  );
};

const MessageDispatcher = defineComponent({
  setup() {
    const { messageQueue } = useMessages();
    const messageUtil = useMessage();
    watch(messageQueue, (after, before) => {
      if (after.length > before.length) {
        while (messageQueue.value.length > 0) {
          const msg = messageQueue.value.pop();
          if (!msg) continue;
          messageUtil.create('', {
            type: msg.type,
            duration: msg.seconds * 1000,
            render: (props) =>
              renderMessage({
                ...props,
                content: () =>
                  h(GlobalMessageContent, null, {
                    default: () => msg.text,
                    details: msg.details ? () => msg.details : undefined,
                  }),
              }),
          });
        }
      }
    });
    return () => null; // nothing to render
  },
});
</script>

<template>
  <n-message-provider placement="bottom" :max="5" keep-alive-on-hover closable>
    <message-dispatcher />
  </n-message-provider>
</template>
