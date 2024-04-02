<script setup lang="ts">
import type { PlainTextContentCreate, PlainTextResourceRead } from '@/api';
import NInputOsk from '@/components/NInputOsk.vue';
import { NFormItem } from 'naive-ui';
import { contentFormRules } from '@/forms/formRules';

const props = defineProps<{
  model: PlainTextContentCreate;
  resource: PlainTextResourceRead;
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
  <!-- TEXT -->
  <n-form-item
    :label="$t('resources.types.plainText.contentFields.text')"
    path="text"
    :rule="contentFormRules.plainText.text"
  >
    <n-input-osk
      type="textarea"
      :rows="3"
      :value="model.text"
      :font="resource.config?.general?.font || undefined"
      :placeholder="$t('resources.types.plainText.contentFields.text')"
      @update:value="(v) => handleUpdate('text', v)"
    />
  </n-form-item>
</template>
