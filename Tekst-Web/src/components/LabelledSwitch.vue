<script setup lang="ts">
import { NFlex, NIcon, NSwitch } from 'naive-ui';
import type { Component } from 'vue';

withDefaults(
  defineProps<{
    label?: string;
    iconOn?: Component;
    iconOff?: Component;
    round?: boolean;
    size?: 'small' | 'medium' | 'large';
    disabled?: boolean;
    loading?: boolean;
    focusable?: boolean;
    checkedValue?: string;
    uncheckedValue?: string;
  }>(),
  {
    label: undefined,
    iconOn: undefined,
    iconOff: undefined,
    round: false,
    size: undefined,
    checkedValue: undefined,
    uncheckedValue: undefined,
  }
);

const model = defineModel<string | number | boolean>();
</script>

<template>
  <n-flex align="center" :wrap="false" class="labelled-switch-container">
    <n-switch
      v-model:value="model"
      :round="round"
      :size="size"
      :disabled="disabled"
      :loading="loading"
      :focusable="focusable"
      :checked-value="checkedValue"
      :unchecked-value="uncheckedValue"
    >
      <template #checked-icon>
        <n-icon :component="iconOn" />
      </template>
      <template #unchecked-icon>
        <n-icon :component="iconOff" />
      </template>
    </n-switch>
    <span class="text-medium" :class="{ translucent: disabled }">
      {{ label }}
    </span>
  </n-flex>
</template>
