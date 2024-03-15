<script setup lang="ts">
import { NFormItem } from 'naive-ui';
import NInputOsk from '@/components/NInputOsk.vue';
import type { PlainTextSearchQuery } from '@/api';

const props = defineProps<{
  value: PlainTextSearchQuery;
}>();
const emit = defineEmits(['update:value']);

function handleUpdate(field: string, value: any) {
  emit('update:value', {
    ...props.value,
    [field]: value,
  });
}
</script>

<template>
  <n-form-item :label="$t('resources.types.plainText.searchFields.text')">
    <n-input-osk
      :value="value.text"
      :placeholder="$t('resources.types.plainText.searchFields.text')"
      @update:value="(v) => handleUpdate('text', v)"
    />
  </n-form-item>
</template>
