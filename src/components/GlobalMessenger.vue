<script setup lang="ts">
import { defineComponent, h } from 'vue';
import {
  NMessageProvider,
  useMessage,
  NAlert,
  useThemeVars,
  type MessageRenderMessage,
} from 'naive-ui';
import { useMessagesStore } from '@/stores';

const themeVars = useThemeVars();

const renderMessage: MessageRenderMessage = (props) => {
  const { type } = props;
  return h(
    'div',
    {
      style: {
        backgroundColor: themeVars.value.bodyColor,
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
        },
      },
      {
        default: () => props.content,
      }
    )
  );
};

const MessageDispatcher = defineComponent({
  setup() {
    const messages = useMessagesStore();
    const messageUtil = useMessage();

    messages.$onAction(({ name, args }) => {
      messageUtil.create(args[0] || name, {
        type: name,
        duration: args[1] || 5000,
        render: renderMessage,
        closable: true,
      });
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
