<script setup lang="ts">
import { NFormItem, NSelect } from 'naive-ui';
import NInputOsk from '@/components/NInputOsk.vue';
import type { AdvancedSearchRequestBody } from '@/api';
import { searchFormRules } from '@/forms/formRules';
import { $t } from '@/i18n';

defineProps<{
  queryIndex: number;
}>();

const comment = defineModel<AdvancedSearchRequestBody['q'][number]['cmn']['cmt']>('comment');
const occurrence = defineModel<AdvancedSearchRequestBody['q'][number]['cmn']['occ']>('occurrence');

const occurrenceOptions = [
  { label: () => $t('search.advancedSearch.occ.should'), value: 'should' },
  { label: () => $t('search.advancedSearch.occ.must'), value: 'must' },
  { label: () => $t('search.advancedSearch.occ.not'), value: 'not' },
];
</script>

<template>
  <n-form-item
    :label="$t('resources.types.common.contentFields.comment')"
    :path="`queries[${queryIndex}].cmn.cmt`"
    :rule="searchFormRules.common.comment"
  >
    <n-input-osk
      v-model="comment"
      :placeholder="$t('resources.types.common.contentFields.comment')"
    />
  </n-form-item>
  <n-form-item :label="$t('search.advancedSearch.occ.label')" :show-feedback="false">
    <n-select v-model:value="occurrence" :options="occurrenceOptions" />
  </n-form-item>
</template>
