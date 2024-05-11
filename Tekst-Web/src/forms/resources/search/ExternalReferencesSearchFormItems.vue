<script setup lang="ts">
import { NFormItem } from 'naive-ui';
import NInputOsk from '@/components/NInputOsk.vue';
import type { ExternalReferencesResourceRead, ExternalReferencesSearchQuery } from '@/api';
import { searchFormRules } from '@/forms/formRules';

defineProps<{
  resource: ExternalReferencesResourceRead;
  queryIndex: number;
}>();

const model = defineModel<ExternalReferencesSearchQuery>({ required: true });

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
    :label="$t('resources.types.externalReferences.contentFields.caption')"
    :path="`queries[${queryIndex}].rts.caption`"
    :rule="searchFormRules.externalReferences.caption"
  >
    <n-input-osk
      :model-value="model.caption"
      :placeholder="$t('resources.types.externalReferences.contentFields.caption')"
      @update:model-value="(v) => handleUpdate('caption', v)"
    />
  </n-form-item>
</template>
