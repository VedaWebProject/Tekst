<script setup lang="ts">
import { useMessages } from '@/composables/messages';
import { $t } from '@/i18n';
import { CopyIcon } from '@/icons';
import { useClipboard } from '@vueuse/core';
import { NButton, NIcon, type ButtonType } from 'naive-ui';

const props = withDefaults(
  defineProps<{
    text?: string | (() => string);
    copiedDuring?: number;
    title?: string;
    showMsg?: boolean;
    type?: ButtonType;
  }>(),
  {
    copiedDuring: 1000,
  }
);

const { message } = useMessages();
const { copy, copied, isSupported } = useClipboard({ copiedDuring: 1000 });

function copyToClipboard() {
  if (!props.text) return;
  const txt = typeof props.text === 'function' ? props.text() : props.text;
  copy(txt);
  if (props.showMsg) {
    message.success($t('common.copiedMsg', { text: txt }));
  }
}
</script>

<template>
  <n-button
    :type="copied ? 'success' : props.type"
    :disabled="!isSupported || !text"
    @click="copyToClipboard"
    :title="title || $t('common.copy')"
    :focusable="false"
  >
    <template #icon>
      <n-icon :component="CopyIcon" />
    </template>
    <slot></slot>
  </n-button>
</template>
