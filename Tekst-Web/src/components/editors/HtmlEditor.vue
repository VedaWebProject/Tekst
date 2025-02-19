<script setup lang="ts">
import type { components } from '@/api/schema';
import { dialogProps } from '@/common';
import WysiwygEditor from '@/components/editors/WysiwygEditor.vue';
import { $t } from '@/i18n';
import { useStateStore } from '@/stores';
import { html } from '@codemirror/lang-html';
import { NTabPane, NTabs, type TabsInst, useDialog } from 'naive-ui';
import { ref, watch } from 'vue';
import { Codemirror } from 'vue-codemirror';

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
const tabsRef = ref<TabsInst>();

const codeEditorExtensions = [html()];
const dialog = useDialog();

function handleChangeTab(value: 'wysiwyg' | 'html') {
  if (value === 'html') {
    // show info about HTML sanitization when switching to HTML mode
    dialog.warning({
      title: $t('general.warning'),
      content: $t('htmlEditor.warnSwitchToHTML'),
      positiveText: $t('general.okAction'),
      negativeText: $t('general.cancelAction'),
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
        <codemirror
          v-model="value"
          :style="{ height: '400px', fontSize: 'var(--font-size-small)' }"
          :indent-with-tab="true"
          :tab-size="4"
          :extensions="codeEditorExtensions"
          @change="emit('input')"
          @focus="emit('focus')"
          @blur="emit('blur')"
        />
      </div>
    </n-tab-pane>
  </n-tabs>
</template>
