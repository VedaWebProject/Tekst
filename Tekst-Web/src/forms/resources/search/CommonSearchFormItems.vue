<script setup lang="ts">
import { NFormItem } from 'naive-ui';
import NInputOsk from '@/components/NInputOsk.vue';
import type { PlainTextSearchQuery } from '@/api';
import LabelledSwitch from '@/components/LabelledSwitch.vue';

defineProps<{
  comment?: PlainTextSearchQuery['cmt'];
  required?: PlainTextSearchQuery['req'];
}>();
defineEmits(['update:comment', 'update:required']);
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
      :value="required"
      :label="$t('search.advancedSearch.required')"
      @update:value="(v) => $emit('update:required', v)"
    />
  </n-form-item>
</template>
