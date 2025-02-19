<script setup lang="ts">
import { NAlert, type MessageType } from 'naive-ui';

defineProps<{
  closable: boolean;
  onClose?: () => void;
  type: MessageType;
}>();
</script>

<template>
  <div class="global-msg-container">
    <n-alert
      :closable="closable"
      :on-close="onClose"
      :type="type === 'loading' ? 'default' : type"
      class="global-msg-alert"
    >
      <div class="text-medium" style="margin: -5px 0">
        <slot></slot>
      </div>
    </n-alert>
  </div>
</template>

<style scoped>
.global-msg-container {
  background-color: #232323;
  border-radius: var(--border-radius);
}

.global-msg-alert {
  box-shadow: var(--n-box-shadow);
  max-width: calc(100vw - 32px);
  width: 512px;
  line-height: 1.5rem;
  padding-right: 36px;
}
</style>
