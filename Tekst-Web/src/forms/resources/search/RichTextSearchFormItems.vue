<script setup lang="ts">
import type { RichTextResourceRead, RichTextSearchQuery } from '@/api';
import NInputOsk from '@/components/NInputOsk.vue';
import { searchFormRules } from '@/forms/formRules';
import { NFormItem } from 'naive-ui';

defineProps<{
  resource: RichTextResourceRead;
  queryIndex: number;
}>();

const model = defineModel<RichTextSearchQuery>({ required: true });

function handleUpdate(field: string, value: unknown) {
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
      :font="resource.config.general.font || undefined"
      :osk-key="resource.config.common.osk || undefined"
      :placeholder="$t('resources.types.richText.searchFields.html')"
      @update:model-value="(v) => handleUpdate('html', v)"
    />
  </n-form-item>
</template>
