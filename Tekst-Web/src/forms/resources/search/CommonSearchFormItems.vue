<script setup lang="ts">
import { NFormItem } from 'naive-ui';
import NInputOsk from '@/components/NInputOsk.vue';
import type { AdvancedSearchRequestBody } from '@/api';
import LabelledSwitch from '@/components/LabelledSwitch.vue';
import { searchFormRules } from '@/forms/formRules';

defineProps<{
  queryIndex: number;
}>();

const comment = defineModel<AdvancedSearchRequestBody['q'][number]['cmn']['cmt']>('comment');
const optional = defineModel<AdvancedSearchRequestBody['q'][number]['cmn']['opt']>('optional');
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
  <n-form-item :show-label="false" :show-feedback="false">
    <labelled-switch v-model="optional" :label="$t('search.advancedSearch.optional')" />
  </n-form-item>
</template>
