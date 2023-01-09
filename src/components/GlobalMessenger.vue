<script setup lang="ts">
import { defineComponent } from 'vue';
import { NMessageProvider, useMessage } from 'naive-ui';
import { useMessagesStore } from '@/stores/messages';

const MessageDispatcher = defineComponent({
  setup() {
    const messages = useMessagesStore();
    const messageUtil = useMessage();

    messages.$onAction(({ args }) => {
      const msg = args?.length && args[0];
      msg && messageUtil.create(msg.text, { type: msg.type ?? 'default' });
    });

    return () => null; // nothing to render
  },
});
</script>

<template>
  <n-message-provider :duration="8000" placement="bottom" :max="5" closable keep-alive-on-hover>
    <MessageDispatcher />
  </n-message-provider>
</template>
