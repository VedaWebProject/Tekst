<script setup lang="ts">
import type { RichTextContentCreate, RichTextResourceRead } from '@/api';
import HtmlEditor from '@/components/editors/HtmlEditor.vue';
import { contentFormRules } from '@/forms/formRules';
import { NFormItem } from 'naive-ui';

defineProps<{
  resource: RichTextResourceRead;
}>();

const model = defineModel<RichTextContentCreate>({ required: true });

function handleUpdate(field: string, value: unknown) {
  model.value = {
    ...model.value,
    [field]: value,
  };
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
      :wysiwyg-font="resource.config.general.font || undefined"
      @update:value="(v: string | null) => handleUpdate('html', v)"
      @update:editor-mode="(v: string) => handleUpdate('editorMode', v)"
    />
  </n-form-item>
</template>
