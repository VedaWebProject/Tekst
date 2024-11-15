<script setup lang="ts">
import type { ImagesResourceRead, ImagesSearchQuery } from '@/api';
import NInputOsk from '@/components/NInputOsk.vue';
import { searchFormRules } from '@/forms/formRules';
import { NFormItem } from 'naive-ui';

defineProps<{
  resource: ImagesResourceRead;
  queryIndex: number;
}>();

const model = defineModel<ImagesSearchQuery>({ required: true });

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
    :label="$t('general.caption')"
    :path="`queries[${queryIndex}].rts.caption`"
    :rule="searchFormRules.images.caption"
  >
    <n-input-osk
      :model-value="model.caption"
      :placeholder="$t('general.caption')"
      @update:model-value="(v) => handleUpdate('caption', v)"
    />
  </n-form-item>
</template>
