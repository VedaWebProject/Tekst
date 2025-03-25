<script setup lang="ts">
import type { components } from '@/api/schema';
import { dialogProps } from '@/common';
import WysiwygEditor from '@/components/editors/WysiwygEditor.vue';
import CodeEditor from '@/components/generic/CodeEditor.vue';
import { $t } from '@/i18n';
import { useStateStore } from '@/stores';
import { html } from '@codemirror/lang-html';
import { NTabPane, NTabs, type TabsInst, useDialog } from 'naive-ui';
import { ref, watch } from 'vue';

type EditorMode = components['schemas']['ClientSegmentRead']['editorMode'];

withDefaults(
  defineProps<{
    toolbarSize?: 'small' | 'medium' | 'large';
    maxChars?: number;
    wysiwygFont?: string;
    rtl?: boolean;
  }>(),
  {
    toolbarSize: 'small',
    maxChars: undefined,
    wysiwygFont: undefined,
  }
);

const emit = defineEmits(['blur', 'focus', 'input']);

const value = defineModel<string>('value');
const editorMode = defineModel<EditorMode>('editorMode', {
  default: 'wysiwyg',
});

const state = useStateStore();
const dialog = useDialog();

const tabsRef = ref<TabsInst>();

function handleChangeTab(value: 'wysiwyg' | 'html') {
  if (value === 'html') {
    // show info about HTML sanitization when switching to HTML mode
    dialog.warning({
      title: $t('common.warning'),
      content: $t('htmlEditor.warnSwitchToHTML'),
      positiveText: $t('common.ok'),
      negativeText: $t('common.cancel'),
      closable: false,
      ...dialogProps,
      onPositiveClick: () => (editorMode.value = value),
    });
  } else {
    // switching to WYSIWYG is a potentially destructive operation
    dialog.warning({
      title: $t('common.warning'),
      content: $t('htmlEditor.warnSwitchToWysiwyg'),
      positiveText: $t('common.yes'),
      negativeText: $t('common.no'),
      closable: false,
      ...dialogProps,
      onPositiveClick: () => (editorMode.value = value),
    });
  }
}

watch(
  () => state.locale,
  () => {
    setTimeout(() => {
      tabsRef.value?.syncBarPosition();
    }, 100);
  }
);
</script>

<template>
  <n-tabs
    ref="tabsRef"
    type="line"
    justify-content="start"
    pane-class="p-0"
    :value="editorMode"
    @update:value="handleChangeTab"
  >
    <n-tab-pane name="wysiwyg" :tab="$t('htmlEditor.wysiwyg')">
      <wysiwyg-editor
        v-model:value="value"
        :max-chars="maxChars"
        :font="wysiwygFont"
        :rtl="rtl"
        @blur="emit('blur')"
        @focus="emit('focus')"
        @input="emit('input')"
      />
    </n-tab-pane>
    <n-tab-pane name="html" :tab="$t('htmlEditor.html')">
      <div class="codemirror-container">
        <code-editor v-model="value" :language="html" :indent-size="4" />
      </div>
    </n-tab-pane>
  </n-tabs>
</template>
