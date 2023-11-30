<script setup lang="ts">
import { NTabs, NTabPane, NInput, useDialog } from 'naive-ui';
import WysiwygEditor from '@/components/WysiwygEditor.vue';
import { $t } from '@/i18n';
import { negativeButtonProps, positiveButtonProps } from './dialogButtonProps';

withDefaults(
  defineProps<{
    value?: string | null;
    toolbarSize?: 'small' | 'medium' | 'large';
    maxChars?: number;
    editorMode: 'wysiwyg' | 'html';
  }>(),
  {
    value: '',
    toolbarSize: 'small',
    maxChars: undefined,
    editorMode: 'wysiwyg',
  }
);

const emit = defineEmits(['update:value', 'update:editorMode', 'blur', 'focus', 'input']);

const dialog = useDialog();

function handleChangeTab(value: 'wysiwyg' | 'html') {
  if (value === 'html') {
    // no harm in switching to HTML
    emit('update:editorMode', value);
    return;
  }
  // switching to WYSIWYG is a potentially destructive operation
  dialog.warning({
    title: $t('general.warning'),
    content: $t('htmlEditor.warnSwitchToWysiwyg'),
    positiveText: $t('general.yesAction'),
    negativeText: $t('general.noAction'),
    positiveButtonProps,
    negativeButtonProps,
    autoFocus: false,
    closable: false,
    onPositiveClick: () => emit('update:editorMode', value),
  });
}
</script>

<template>
  <n-tabs
    type="line"
    size="large"
    justify-content="start"
    :value="editorMode"
    @update:value="handleChangeTab"
  >
    <n-tab-pane name="wysiwyg" :tab="$t('htmlEditor.wysiwyg')">
      <WysiwygEditor
        :value="value"
        :max-chars="maxChars"
        @update:value="emit('update:value', $event)"
        @blur="emit('blur')"
        @focus="emit('focus')"
        @input="emit('input')"
      />
    </n-tab-pane>
    <n-tab-pane name="html" :tab="$t('htmlEditor.html')">
      <n-input
        :value="value"
        type="textarea"
        :rows="8"
        placeholder=""
        :maxlength="maxChars"
        show-count
        style="font-family: 'Courier New', Courier, monospace"
        @update:value="emit('update:value', $event)"
        @blur="emit('blur')"
        @focus="emit('focus')"
        @input="emit('input')"
      />
    </n-tab-pane>
  </n-tabs>
</template>

<style scoped></style>
