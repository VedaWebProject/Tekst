<script setup lang="ts">
import { NFormItem } from 'naive-ui';
import NInputOsk from '@/components/NInputOsk.vue';
import type { AdvancedSearchRequestBody } from '@/api';
import LabelledSwitch from '@/components/LabelledSwitch.vue';

defineProps<{
  comment?: AdvancedSearchRequestBody['q'][number]['cmn']['cmt'];
  optional?: AdvancedSearchRequestBody['q'][number]['cmn']['opt'];
}>();
defineEmits(['update:comment', 'update:optional']);
</script>

<template>
  <n-form-item :label="$t('resources.types.common.contentFields.comment')">
    <n-input-osk
      :value="comment"
      :placeholder="$t('resources.types.common.contentFields.comment')"
      @update:value="(v) => $emit('update:comment', v)"
    />
  </n-form-item>
  <n-form-item :show-label="false" :show-feedback="false">
    <labelled-switch
      :value="optional"
      :label="$t('search.advancedSearch.optional')"
      @update:value="(v) => $emit('update:optional', v)"
    />
  </n-form-item>
</template>
