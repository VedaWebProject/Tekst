<script setup lang="ts">
import type { PlaintextContentCreate } from '@/api';
import { NInput, NFormItem } from 'naive-ui';

const props = defineProps<{
  model?: PlaintextContentCreate;
}>();

const emits = defineEmits(['update:model']);

function handleUpdate(field: string, value: any) {
  emits('update:model', {
    ...props.model,
    [field]: value,
  });
}
</script>

<template>
  <template v-if="model">
    <!-- TEXT -->
    <n-form-item :label="$t('resources.types.plaintext.contentFields.text')" path="text">
      <n-input
        type="textarea"
        :rows="3"
        :value="model.text"
        :placeholder="$t('resources.types.plaintext.contentFields.text')"
        @update:value="(v) => handleUpdate('text', v)"
      />
    </n-form-item>
  </template>
</template>
