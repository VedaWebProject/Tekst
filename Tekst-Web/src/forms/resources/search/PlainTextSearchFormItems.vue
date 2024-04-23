<script setup lang="ts">
import { NFormItem } from 'naive-ui';
import NInputOsk from '@/components/NInputOsk.vue';
import type { PlainTextResourceRead, PlainTextSearchQuery } from '@/api';
import { searchFormRules } from '@/forms/formRules';

defineProps<{
  resource: PlainTextResourceRead;
  queryIndex: number;
}>();

const model = defineModel<PlainTextSearchQuery>({ required: true });

function handleUpdate(field: string, value: any) {
  model.value = {
    ...model.value,
    [field]: value,
  };
}
</script>

<template>
  <n-form-item
    ignore-path-change
    :label="$t('resources.types.plainText.searchFields.text')"
    :path="`queries[${queryIndex}].rts.text`"
    :rule="searchFormRules.plainText.text"
  >
    <n-input-osk
      :model-value="model.text"
      :placeholder="$t('resources.types.plainText.searchFields.text')"
      @update:model-value="(v) => handleUpdate('text', v)"
    />
  </n-form-item>
</template>
