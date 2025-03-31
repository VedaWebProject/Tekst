<script setup lang="ts">
import type { RichTextContentCreate, RichTextResourceRead } from '@/api';
import HtmlEditor from '@/components/editors/HtmlEditor.vue';
import { contentFormRules } from '@/forms/formRules';
import { NFormItem } from 'naive-ui';

defineProps<{
  resource: RichTextResourceRead;
}>();

const model = defineModel<RichTextContentCreate>({ required: true });
</script>

<template>
  <!-- HTML -->
  <n-form-item
    :label="$t('resources.types.richText.contentFields.html')"
    path="html"
    :rule="contentFormRules.richText.html"
  >
    <html-editor
      v-model:value="model.html"
      v-model:editor-mode="model.editorMode"
      toolbar-size="medium"
      :max-chars="102400"
      :wysiwyg-font="resource.config.general.font || undefined"
      :rtl="resource.config.general.rtl"
    />
  </n-form-item>
</template>
