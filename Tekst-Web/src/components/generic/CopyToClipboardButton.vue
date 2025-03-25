<script setup lang="ts">
import { $t } from '@/i18n';
import { CopyIcon } from '@/icons';
import { useClipboard } from '@vueuse/core';
import { NButton, NIcon } from 'naive-ui';
import type { Type } from 'naive-ui/es/button/src/interface';
import { useAttrs } from 'vue';

const props = withDefaults(
  defineProps<{
    text?: string | (() => string);
    copiedDuring?: number;
    title?: string;
  }>(),
  {
    copiedDuring: 1000,
  }
);

const attrs: Record<string, unknown> = useAttrs();
const { copy, copied, isSupported } = useClipboard({ copiedDuring: 1000 });

function copyToClipboard() {
  if (!props.text) return;
  const txt = typeof props.text === 'function' ? props.text() : props.text;
  copy(txt);
}
</script>

<template>
  <n-button
    :type="copied ? 'success' : (attrs.type as Type | undefined)"
    :disabled="!isSupported || !text"
    @click="copyToClipboard"
    :title="title || $t('common.copy')"
  >
    <template #icon>
      <n-icon :component="CopyIcon" />
    </template>
    <slot></slot>
  </n-button>
</template>
