<script setup lang="ts">
import type { PlainTextContentCreate, PlainTextResourceRead } from '@/api';
import OskInput from '@/components/OskInput.vue';
import { contentFormRules } from '@/forms/formRules';
import { NFormItem } from 'naive-ui';

defineProps<{
  resource: PlainTextResourceRead;
}>();

const model = defineModel<PlainTextContentCreate>({ required: true });
</script>

<template>
  <!-- TEXT -->
  <n-form-item
    :label="$t('resources.types.plainText.contentFields.text')"
    path="text"
    :rule="contentFormRules.plainText.text"
  >
    <osk-input
      v-model="model.text"
      type="textarea"
      :rows="3"
      :font="resource.config.general.font || undefined"
      :osk-key="resource.config.general.osk || undefined"
      :placeholder="$t('resources.types.plainText.contentFields.text')"
      :dir="resource.config.general.rtl ? 'rtl' : undefined"
    />
  </n-form-item>
</template>
