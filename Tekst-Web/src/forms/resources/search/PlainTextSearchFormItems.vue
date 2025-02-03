<script setup lang="ts">
import type { PlainTextResourceRead, PlainTextSearchQuery } from '@/api';
import NInputOsk from '@/components/NInputOsk.vue';
import { searchFormRules } from '@/forms/formRules';
import { NFormItem } from 'naive-ui';

defineProps<{
  resource: PlainTextResourceRead;
  queryIndex: number;
}>();

const model = defineModel<PlainTextSearchQuery>({ required: true });
</script>

<template>
  <n-form-item
    ignore-path-change
    :label="$t('resources.types.plainText.searchFields.text')"
    :path="`queries[${queryIndex}].rts.text`"
    :rule="searchFormRules.plainText.text"
  >
    <n-input-osk
      v-model="model.text"
      :font="resource.config.general.font || undefined"
      :osk-key="resource.config.common.osk || undefined"
      :placeholder="$t('resources.types.plainText.searchFields.text')"
    />
  </n-form-item>
</template>
