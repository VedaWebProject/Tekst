<script setup lang="ts">
import type { AdvancedSearchRequestBody } from '@/api';
import NInputOsk from '@/components/NInputOsk.vue';
import { searchFormRules } from '@/forms/formRules';
import { $t } from '@/i18n';
import { NFormItem } from 'naive-ui';

defineProps<{
  queryIndex: number;
}>();

const comment =
  defineModel<NonNullable<AdvancedSearchRequestBody['q']>[number]['cmn']['cmt']>('comment');
</script>

<template>
  <n-form-item
    :label="$t('common.comment')"
    :path="`queries[${queryIndex}].cmn.cmt`"
    :rule="searchFormRules.common.comment"
  >
    <n-input-osk v-model="comment" :placeholder="$t('common.comment')" />
  </n-form-item>
</template>
