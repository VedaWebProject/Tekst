<script setup lang="ts">
import type { PlainTextContentCreate } from '@/api';
import { NInput, NFormItem } from 'naive-ui';

const props = defineProps<{
  model?: PlainTextContentCreate;
}>();

const emit = defineEmits(['update:model']);

function handleUpdate(field: string, value: any) {
  emit('update:model', {
    ...props.model,
    [field]: value,
  });
}
</script>

<template>
  <template v-if="model">
    <!-- TEXT -->
    <n-form-item :label="$t('resources.types.plainText.contentFields.text')" path="text">
      <n-input
        type="textarea"
        :rows="3"
        :value="model.text"
        :placeholder="$t('resources.types.plainText.contentFields.text')"
        @update:value="(v) => handleUpdate('text', v)"
      />
    </n-form-item>
  </template>
</template>
