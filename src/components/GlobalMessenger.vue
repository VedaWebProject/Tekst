<script setup lang="ts">
import { defineComponent, watch } from 'vue';
import { NMessageProvider, useMessage } from 'naive-ui';
import { useMessagesStore } from '@/stores/messages';

const MessageDispatcher = defineComponent({
  setup() {
    const messages = useMessagesStore();
    const messageUtil = useMessage();

    // react to message queue updates
    watch(messages.queue, (queue) => {
      const msg = queue.shift(); // get next message
      msg && messageUtil.create(msg.text, { type: msg.type ?? 'default' }); // msg might be undefined
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
