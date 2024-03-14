<script setup lang="ts">
import { NFormItem } from 'naive-ui';
import NInputOsk from '@/components/NInputOsk.vue';
import type { PlainTextSearchQuery } from '@/api';

const props = defineProps<{
  model: PlainTextSearchQuery;
}>();
const emit = defineEmits(['update:model']);

function handleUpdate(field: string, value: any) {
  emit('update:model', {
    ...props.model,
    [field]: value,
  });
}
</script>

<template>
  <n-form-item :label="$t('resources.types.plainText.searchFields.text')">
    <n-input-osk
      :value="model.text"
      :placeholder="$t('resources.types.plainText.searchFields.text')"
      @update:value="(v) => handleUpdate('text', v)"
    />
  </n-form-item>
  <n-form-item :label="$t('resources.types.common.contentFields.comment')">
    <n-input-osk
      :value="model.comment"
      :placeholder="$t('resources.types.common.contentFields.comment')"
      @update:value="(v) => handleUpdate('comment', v)"
    />
  </n-form-item>
</template>
