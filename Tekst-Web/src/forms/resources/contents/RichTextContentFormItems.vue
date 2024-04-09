<script setup lang="ts">
import type { RichTextContentCreate, RichTextResourceRead } from '@/api';
import HtmlEditor from '@/components/editors/HtmlEditor.vue';
import { NFormItem } from 'naive-ui';
import { contentFormRules } from '@/forms/formRules';

const props = defineProps<{
  model: RichTextContentCreate;
  resource: RichTextResourceRead;
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
  <!-- HTML -->
  <n-form-item
    :label="$t('resources.types.richText.contentFields.html')"
    path="html"
    :rule="contentFormRules.richText.html"
  >
    <html-editor
      :value="model.html"
      :editor-mode="model.editorMode ?? 'wysiwyg'"
      toolbar-size="medium"
      :max-chars="102400"
      :wysiwyg-font="resource.config?.general?.font || undefined"
      @update:value="(v) => handleUpdate('html', v)"
      @update:editor-mode="(v) => handleUpdate('editorMode', v)"
    />
  </n-form-item>
</template>
