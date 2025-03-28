<script setup lang="ts">
import type { ExternalReferencesResourceRead, ExternalReferencesSearchQuery } from '@/api';
import OskInput from '@/components/OskInput.vue';
import { searchFormRules } from '@/forms/formRules';
import { NFormItem } from 'naive-ui';

defineProps<{
  resource: ExternalReferencesResourceRead;
  queryIndex: number;
}>();

const model = defineModel<ExternalReferencesSearchQuery>({ required: true });
</script>

<template>
  <n-form-item
    ignore-path-change
    :label="$t('resources.types.externalReferences.searchFields.text')"
    :path="`queries[${queryIndex}].rts.text`"
    :rule="searchFormRules.externalReferences.text"
  >
    <osk-input
      v-model="model.text"
      :font="resource.config.general.font || undefined"
      :osk-key="resource.config.common.osk || undefined"
      :placeholder="$t('resources.types.externalReferences.searchFields.text')"
    />
  </n-form-item>
</template>
