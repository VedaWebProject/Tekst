<script setup lang="ts">
import { NFormItem } from 'naive-ui';
import NInputOsk from '@/components/NInputOsk.vue';
import type { RichTextSearchQuery } from '@/api';

const props = defineProps<{
  value: RichTextSearchQuery;
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
  <n-form-item :label="$t('resources.types.richText.searchFields.html')">
    <n-input-osk
      :value="value.html"
      :placeholder="$t('resources.types.richText.searchFields.html')"
      @update:value="(v) => handleUpdate('html', v)"
    />
  </n-form-item>
</template>
