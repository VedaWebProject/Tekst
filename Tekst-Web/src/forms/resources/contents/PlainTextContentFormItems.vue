<script setup lang="ts">
import type { PlainTextContentCreate, PlainTextResourceRead } from '@/api';
import NInputOsk from '@/components/NInputOsk.vue';
import { contentFormRules } from '@/forms/formRules';
import { NFormItem } from 'naive-ui';

defineProps<{
  resource: PlainTextResourceRead;
}>();

const model = defineModel<PlainTextContentCreate>({ required: true });

function handleUpdate(field: string, value: unknown) {
  model.value = {
    ...model.value,
    [field]: value,
  };
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
      :model-value="model.text"
      :font="resource.config.general.font || undefined"
      :osk-key="resource.config.common.osk || undefined"
      :placeholder="$t('resources.types.plainText.contentFields.text')"
      @update:model-value="(v) => handleUpdate('text', v)"
      :dir="resource.config.common.rtl ? 'rtl' : undefined"
    />
  </n-form-item>
</template>
