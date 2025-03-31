<script setup lang="ts">
import type { PlainTextResourceRead, PlainTextSearchQuery } from '@/api';
import OskInput from '@/components/OskInput.vue';
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
    :label="$t('common.text')"
    :path="`queries[${queryIndex}].rts.text`"
    :rule="searchFormRules.plainText.text"
  >
    <osk-input
      v-model="model.text"
      :font="resource.config.general.font || undefined"
      :osk-key="resource.config.general.osk || undefined"
      :placeholder="$t('common.text')"
    />
  </n-form-item>
</template>
