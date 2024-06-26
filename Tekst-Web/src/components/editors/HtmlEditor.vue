<script setup lang="ts">
import { NTabs, NTabPane, NInput, useDialog } from 'naive-ui';
import WysiwygEditor from '@/components/editors/WysiwygEditor.vue';
import { $t } from '@/i18n';
import { dialogProps } from '@/common';

withDefaults(
  defineProps<{
    toolbarSize?: 'small' | 'medium' | 'large';
    maxChars?: number;
    wysiwygFont?: string;
  }>(),
  {
    toolbarSize: 'small',
    maxChars: undefined,
    editorMode: 'wysiwyg',
    wysiwygFont: undefined,
  }
);

const emit = defineEmits(['blur', 'focus', 'input']);

const value = defineModel<string | null>('value');
const editorMode = defineModel<'wysiwyg' | 'html'>('editorMode');

const dialog = useDialog();

function handleChangeTab(value: 'wysiwyg' | 'html') {
  if (value === 'html') {
    // show info about HTML sanitization when switching to HTML mode
    dialog.warning({
      title: $t('general.warning'),
      content: $t('htmlEditor.warnSwitchToHTML'),
      positiveText: $t('general.okAction'),
      negativeText: $t('general.cancelAction'),
      autoFocus: false,
      closable: false,
      ...dialogProps,
      onPositiveClick: () => (editorMode.value = value),
    });
  } else {
    // switching to WYSIWYG is a potentially destructive operation
    dialog.warning({
      title: $t('general.warning'),
      content: $t('htmlEditor.warnSwitchToWysiwyg'),
      positiveText: $t('general.yesAction'),
      negativeText: $t('general.noAction'),
      autoFocus: false,
      closable: false,
      ...dialogProps,
      onPositiveClick: () => (editorMode.value = value),
    });
  }
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
      <wysiwyg-editor
        v-model:value="value"
        :max-chars="maxChars"
        :font="wysiwygFont"
        @blur="emit('blur')"
        @focus="emit('focus')"
        @input="emit('input')"
      />
    </n-tab-pane>
    <n-tab-pane name="html" :tab="$t('htmlEditor.html')">
      <n-input
        v-model:value="value"
        type="textarea"
        :rows="8"
        placeholder=""
        :maxlength="maxChars"
        show-count
        style="font-family: 'Courier New', Courier, monospace"
        @blur="emit('blur')"
        @focus="emit('focus')"
        @input="emit('input')"
      />
    </n-tab-pane>
  </n-tabs>
</template>

<style scoped></style>
