<script setup lang="ts">
import type { RichTextResourceRead, RichTextSearchQuery } from '@/api';
import OskInput from '@/components/OskInput.vue';
import { searchFormRules } from '@/forms/formRules';
import { NFormItem } from 'naive-ui';

defineProps<{
  resource: RichTextResourceRead;
  queryIndex: number;
}>();

const model = defineModel<RichTextSearchQuery>({ required: true });
</script>

<template>
  <n-form-item
    ignore-path-change
    :label="$t('common.text')"
    :path="`queries[${queryIndex}].rts.html`"
    :rule="searchFormRules.richText.html"
  >
    <osk-input
      v-model="model.html"
      :font="resource.config.general.font || undefined"
      :osk-key="resource.config.general.osk || undefined"
      :placeholder="$t('common.text')"
    />
  </n-form-item>
</template>
