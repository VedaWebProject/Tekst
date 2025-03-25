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
</script>

<template>
  <n-form-item
    ignore-path-change
    :label="$t('common.text')"
    :path="`queries[${queryIndex}].rts.html`"
    :rule="searchFormRules.richText.html"
  >
    <n-input-osk
      v-model="model.html"
      :font="resource.config.general.font || undefined"
      :osk-key="resource.config.common.osk || undefined"
      :placeholder="$t('common.text')"
    />
  </n-form-item>
</template>
