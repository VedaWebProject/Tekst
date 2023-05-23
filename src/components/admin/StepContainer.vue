<script setup lang="ts">
import { NSpace, NButton } from 'naive-ui';

defineProps<{
  currentStep: number;
  stepNo: number;
  submitButtonLabel: string;
}>();

defineEmits(['submit']);
</script>

<template>
  <div v-show="stepNo === currentStep">
    <slot></slot>
    <n-space :size="12" justify="end" style="margin-top: 0.5rem">
      <n-button block type="primary" @click="$emit('submit')">
        {{ submitButtonLabel }}
      </n-button>
    </n-space>
  </div>
</template>
