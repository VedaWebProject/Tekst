<script setup lang="ts">
import { NFormItem } from 'naive-ui';
import NInputOsk from '@/components/NInputOsk.vue';
import type { ImagesResourceRead, ImagesSearchQuery } from '@/api';
import { searchFormRules } from '@/forms/formRules';

defineProps<{
  resource: ImagesResourceRead;
  queryIndex: number;
}>();

const model = defineModel<ImagesSearchQuery>({ required: true });

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
    :label="$t('resources.types.images.contentFields.caption')"
    :path="`queries[${queryIndex}].rts.caption`"
    :rule="searchFormRules.images.caption"
  >
    <n-input-osk
      :model-value="model.caption"
      :placeholder="$t('resources.types.images.contentFields.caption')"
      @update:model-value="(v) => handleUpdate('caption', v)"
    />
  </n-form-item>
</template>
