<script setup lang="ts">
import { NSwitch, NSpace } from 'naive-ui';

withDefaults(
  defineProps<{
    value?: string | number | boolean | undefined;
    label?: string;
    round?: boolean;
    size?: 'small' | 'medium' | 'large';
    disabled?: boolean;
    loading?: boolean;
    focusable?: boolean;
  }>(),
  {
    value: undefined,
    label: undefined,
    round: false,
    size: undefined,
  }
);

defineEmits(['update:value']);
</script>

<template>
  <n-space align="center" :wrap="false">
    <n-switch
      :value="value"
      :round="round"
      :size="size"
      :disabled="disabled"
      :loading="loading"
      :focusable="focusable"
      @update:value="(v) => $emit('update:value', v)"
    />
    <span style="font-size: var(--font-size-medium)" :class="{ translucent: disabled }">{{
      label
    }}</span>
  </n-space>
</template>
