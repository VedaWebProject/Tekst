<script setup lang="ts">
import { NFormItem } from 'naive-ui';
import NInputOsk from '@/components/NInputOsk.vue';
import type { RichTextResourceRead, RichTextSearchQuery } from '@/api';
import { searchFormRules } from '@/forms/formRules';

defineProps<{
  resource: RichTextResourceRead;
  queryIndex: number;
}>();

const model = defineModel<RichTextSearchQuery>({ required: true });

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
    :label="$t('resources.types.richText.searchFields.html')"
    :path="`queries[${queryIndex}].rts.html`"
    :rule="searchFormRules.richText.html"
  >
    <n-input-osk
      :model-value="model.html"
      :placeholder="$t('resources.types.richText.searchFields.html')"
      @update:model-value="(v) => handleUpdate('html', v)"
    />
  </n-form-item>
</template>
