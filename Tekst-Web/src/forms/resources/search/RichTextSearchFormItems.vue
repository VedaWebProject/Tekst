<script setup lang="ts">
import { NFormItem } from 'naive-ui';
import NInputOsk from '@/components/NInputOsk.vue';
import type { RichTextResourceRead, RichTextSearchQuery } from '@/api';
import { searchFormRules } from '@/forms/formRules';

const props = defineProps<{
  value: RichTextSearchQuery;
  resource: RichTextResourceRead;
  queryIndex: number;
}>();
const emit = defineEmits(['update:value']);

function handleUpdate(field: string, value: any) {
  emit('update:value', {
    ...props.value,
    [field]: value,
  });
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
      :value="value.html"
      :placeholder="$t('resources.types.richText.searchFields.html')"
      @update:value="(v) => handleUpdate('html', v)"
    />
  </n-form-item>
</template>
