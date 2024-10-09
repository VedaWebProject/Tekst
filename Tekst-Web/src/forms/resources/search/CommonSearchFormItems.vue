<script setup lang="ts">
import { NFormItem } from 'naive-ui';
import NInputOsk from '@/components/NInputOsk.vue';
import type { AdvancedSearchRequestBody } from '@/api';
import { searchFormRules } from '@/forms/formRules';
import { $t } from '@/i18n';

defineProps<{
  queryIndex: number;
}>();

const comment =
  defineModel<NonNullable<AdvancedSearchRequestBody['q']>[number]['cmn']['cmt']>('comment');
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
</template>
