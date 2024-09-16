<script setup lang="ts">
import { NFormItem, NSelect } from 'naive-ui';
import type { AdvancedSearchRequestBody } from '@/api';
import { $t } from '@/i18n';

defineProps<{
  queryIndex: number;
}>();

const occurrence = defineModel<AdvancedSearchRequestBody['q'][number]['cmn']['occ']>('occurrence');

const occurrenceOptions = [
  { label: () => $t('search.advancedSearch.occ.should'), value: 'should' },
  { label: () => $t('search.advancedSearch.occ.must'), value: 'must' },
  { label: () => $t('search.advancedSearch.occ.not'), value: 'not' },
];
</script>

<template>
  <n-form-item :show-label="false">
    <n-select
      v-model:value="occurrence"
      :options="occurrenceOptions"
      :title="$t('search.advancedSearch.occ.label')"
    />
  </n-form-item>
</template>
