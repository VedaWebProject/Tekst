<script setup lang="ts">
import { defineComponent, h, watch } from 'vue';
import {
  NMessageProvider,
  useMessage,
  NAlert,
  useThemeVars,
  type MessageRenderMessage,
} from 'naive-ui';
import { useMessages } from '@/messages';
import Color from 'color';
import type { RenderMessageProps } from 'naive-ui/es/message/src/types';

const themeVars = useThemeVars();

const renderMessage: MessageRenderMessage = (props: RenderMessageProps) => {
  const { type } = props;
  return h(
    'div',
    {
      style: {
        backgroundColor: Color(themeVars.value.bodyColor).lighten(0.8).hex(),
        borderRadius: themeVars.value.borderRadius,
      },
    },
    h(
      NAlert,
      {
        closable: props.closable,
        onClose: props.onClose,
        type: type === 'loading' ? 'default' : type,
        showIcon: true,
        style: {
          boxShadow: 'var(--n-box-shadow)',
          maxWidth: 'calc(100vw - 32px)',
          width: '512px',
          lineHeight: '1.5rem',
          paddingRight: '36px',
        },
      },
      {
        default: () =>
          h(
            'div',
            {
              style: {
                fontSize: 'var(--app-ui-font-size-small)',
                margin: '-5px 0', // a dirty, but effective hack
              },
            },
            {
              default: () => props.content,
            }
          ),
      }
    )
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
          msg &&
            messageUtil.create(msg.text, {
              type: msg.type,
              duration: msg.durationSeconds * 1000,
              render: renderMessage,
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
    <MessageDispatcher />
  </n-message-provider>
</template>
