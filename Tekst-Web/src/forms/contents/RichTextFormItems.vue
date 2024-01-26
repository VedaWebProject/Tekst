<script setup lang="ts">
import type { RichTextContentCreate } from '@/api';
import HtmlEditor from '@/components/editors/HtmlEditor.vue';
import { NFormItem } from 'naive-ui';

const props = defineProps<{
  model?: RichTextContentCreate;
}>();

const emits = defineEmits(['update:model']);

function handleUpdate(field: string, value: any) {
  emits('update:model', {
    ...props.model,
    [field]: value,
  });
}
</script>

<template>
  <template v-if="model">
    <!-- HTML -->
    <n-form-item :label="$t('resources.types.richText.contentFields.html')" path="html">
      <HtmlEditor
        :value="model.html"
        toolbar-size="medium"
        :max-chars="102400"
        @update:value="(v) => handleUpdate('html', v)"
      />
    </n-form-item>
  </template>
</template>
