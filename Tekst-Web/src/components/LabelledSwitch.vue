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
    checkedValue?: string;
    uncheckedValue?: string;
  }>(),
  {
    value: undefined,
    label: undefined,
    round: false,
    size: undefined,
    checkedValue: undefined,
    uncheckedValue: undefined,
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
      :checked-value="checkedValue"
      :unchecked-value="uncheckedValue"
      @update:value="(v) => $emit('update:value', v)"
    />
    <span class="text-medium" :class="{ translucent: disabled }">
      {{ label }}
    </span>
  </n-space>
</template>
