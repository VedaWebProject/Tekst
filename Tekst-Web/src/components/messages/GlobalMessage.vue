<script setup lang="ts">
import { NAlert, useThemeVars, type MessageType } from 'naive-ui';
import Color from 'color';

defineProps<{
  closable: boolean;
  onClose?: () => void;
  type: MessageType;
}>();

const themeVars = useThemeVars();
</script>

<template>
  <div
    :style="{
      backgroundColor: Color(themeVars.bodyColor).lighten(0.8).hex(),
      borderRadius: themeVars.borderRadius,
    }"
  >
    <n-alert
      :closable="closable"
      :on-close="onClose"
      :type="type === 'loading' ? 'default' : type"
      :style="{
        boxShadow: 'var(--n-box-shadow)',
        maxWidth: 'calc(100vw - 32px)',
        width: '512px',
        lineHeight: '1.5rem',
        paddingRight: '36px',
      }"
    >
      <div class="text-small" style="margin: -5px 0">
        <slot></slot>
      </div>
    </n-alert>
  </div>
</template>
