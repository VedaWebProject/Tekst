<script setup lang="ts">
import type { ExternalReferencesResourceRead, ExternalReferencesSearchQuery } from '@/api';
import NInputOsk from '@/components/NInputOsk.vue';
import { searchFormRules } from '@/forms/formRules';
import { NFormItem } from 'naive-ui';

defineProps<{
  resource: ExternalReferencesResourceRead;
  queryIndex: number;
}>();

const model = defineModel<ExternalReferencesSearchQuery>({ required: true });

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
    :label="$t('resources.types.externalReferences.searchFields.text')"
    :path="`queries[${queryIndex}].rts.text`"
    :rule="searchFormRules.externalReferences.text"
  >
    <n-input-osk
      :model-value="model.text"
      :font="resource.config.general.font || undefined"
      :osk-key="resource.config.common.osk || undefined"
      :placeholder="$t('resources.types.externalReferences.searchFields.text')"
      @update:model-value="(v) => handleUpdate('text', v)"
    />
  </n-form-item>
</template>
