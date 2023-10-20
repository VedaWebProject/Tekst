<script setup lang="ts">
import { NButton, NIcon } from 'naive-ui';
import { useEditor, EditorContent } from '@tiptap/vue-3';
import StarterKit from '@tiptap/starter-kit';
import { computed, onUnmounted, watch, h, type Component, type CSSProperties, ref } from 'vue';

import FormatBoldOutlined from '@vicons/material/FormatBoldOutlined';
import FormatItalicOutlined from '@vicons/material/FormatItalicOutlined';
import CodeOutlined from '@vicons/material/CodeOutlined';
import FormatClearOutlined from '@vicons/material/FormatClearOutlined';
import FormatQuoteOutlined from '@vicons/material/FormatQuoteOutlined';
import FormatListBulletedOutlined from '@vicons/material/FormatListBulletedOutlined';
import FormatListNumberedOutlined from '@vicons/material/FormatListNumberedOutlined';
import HorizontalRuleOutlined from '@vicons/material/HorizontalRuleOutlined';
import KeyboardReturnOutlined from '@vicons/material/KeyboardReturnOutlined';
import UndoOutlined from '@vicons/material/UndoOutlined';
import RedoOutlined from '@vicons/material/RedoOutlined';
import HtmlOutlined from '@vicons/material/HtmlOutlined';

const props = withDefaults(
  defineProps<{
    document: string;
    toolbarSize?: 'small' | 'medium' | 'large';
    maxChars?: number;
  }>(),
  {
    toolbarSize: 'small',
    maxChars: undefined,
  }
);

const emit = defineEmits(['update:document']);

const showHtml = ref(false);

const editor = useEditor({
  content: props.document,
  extensions: [
    StarterKit.configure({
      heading: {
        levels: [1, 2, 3, 4],
      },
    }),
  ],
  injectCSS: false,
  onUpdate: () => {
    emit('update:document', editor.value?.getHTML());
  },
  editorProps: {
    attributes: {
      style: `
        outline: 0;
        margin: .5rem 0;
        padding: 0 .5rem;
        border: 1px solid var(--text-color);
        border-radius: var(--app-ui-border-radius);
      `,
    },
  },
});

const toolbarStyles = computed<CSSProperties>(() => ({
  fontSize: { small: 18, medium: 22, large: 24 }[props.toolbarSize],
}));

function renderToolbarIcon(icon: Component) {
  return () =>
    h(
      NIcon,
      { size: toolbarStyles.value.fontSize },
      {
        default: () => h(icon),
      }
    );
}

watch(
  () => props.document,
  (newDocument) => {
    if (editor.value?.getHTML() === newDocument) return;
    editor.value?.commands.setContent(newDocument, false);
  }
);

onUnmounted(() => {
  editor.value?.destroy();
});
</script>

<template>
  <div>
    <div v-if="editor" class="toolbar">
      <n-button
        :style="toolbarStyles"
        :size="toolbarSize"
        :disabled="!editor.can().chain().focus().toggleBold().run()"
        :type="(editor.isActive('bold') && 'primary') || undefined"
        :render-icon="renderToolbarIcon(FormatBoldOutlined)"
        @click="editor.chain().focus().toggleBold().run()"
      />
      <n-button
        :style="toolbarStyles"
        :size="toolbarSize"
        :disabled="!editor.can().chain().focus().toggleItalic().run()"
        :class="{ 'is-active': editor.isActive('italic') }"
        :render-icon="renderToolbarIcon(FormatItalicOutlined)"
        @click="editor.chain().focus().toggleItalic().run()"
      />
      <n-button
        :style="toolbarStyles"
        :size="toolbarSize"
        :disabled="!editor.can().chain().focus().toggleCode().run()"
        :class="{ 'is-active': editor.isActive('code') }"
        :render-icon="renderToolbarIcon(CodeOutlined)"
        @click="editor.chain().focus().toggleCode().run()"
      />
      <n-button
        :style="toolbarStyles"
        :size="toolbarSize"
        :render-icon="renderToolbarIcon(FormatClearOutlined)"
        @click="
          () => {
            editor?.chain().focus().unsetAllMarks().run();
            editor?.chain().focus().clearNodes().run();
          }
        "
      />
      <n-button
        :style="toolbarStyles"
        :size="toolbarSize"
        :class="{ 'is-active': editor.isActive('heading', { level: 1 }) }"
        @click="editor.chain().focus().toggleHeading({ level: 1 }).run()"
      >
        H1
      </n-button>
      <n-button
        :style="toolbarStyles"
        :size="toolbarSize"
        :class="{ 'is-active': editor.isActive('heading', { level: 2 }) }"
        @click="editor.chain().focus().toggleHeading({ level: 2 }).run()"
      >
        H2
      </n-button>
      <n-button
        :style="toolbarStyles"
        :size="toolbarSize"
        :class="{ 'is-active': editor.isActive('heading', { level: 3 }) }"
        @click="editor.chain().focus().toggleHeading({ level: 3 }).run()"
      >
        H3
      </n-button>
      <n-button
        :style="toolbarStyles"
        :size="toolbarSize"
        :class="{ 'is-active': editor.isActive('heading', { level: 4 }) }"
        @click="editor.chain().focus().toggleHeading({ level: 4 }).run()"
      >
        H4
      </n-button>
      <n-button
        :style="toolbarStyles"
        :size="toolbarSize"
        :class="{ 'is-active': editor.isActive('bulletList') }"
        :render-icon="renderToolbarIcon(FormatListBulletedOutlined)"
        @click="editor.chain().focus().toggleBulletList().run()"
      />
      <n-button
        :style="toolbarStyles"
        :size="toolbarSize"
        :class="{ 'is-active': editor.isActive('orderedList') }"
        :render-icon="renderToolbarIcon(FormatListNumberedOutlined)"
        @click="editor.chain().focus().toggleOrderedList().run()"
      />
      <n-button
        :style="toolbarStyles"
        :size="toolbarSize"
        :class="{ 'is-active': editor.isActive('codeBlock') }"
        :render-icon="renderToolbarIcon(CodeOutlined)"
        @click="editor.chain().focus().toggleCodeBlock().run()"
      />
      <n-button
        :style="toolbarStyles"
        :size="toolbarSize"
        :secondary="editor.isActive('blockquote')"
        :render-icon="renderToolbarIcon(FormatQuoteOutlined)"
        @click="editor.chain().focus().toggleBlockquote().run()"
      />
      <n-button
        :style="toolbarStyles"
        :size="toolbarSize"
        :render-icon="renderToolbarIcon(HorizontalRuleOutlined)"
        @click="editor.chain().focus().setHorizontalRule().run()"
      />
      <n-button
        :style="toolbarStyles"
        :size="toolbarSize"
        :render-icon="renderToolbarIcon(KeyboardReturnOutlined)"
        @click="editor.chain().focus().setHardBreak().run()"
      />
      <n-button
        :style="toolbarStyles"
        :size="toolbarSize"
        :disabled="!editor.can().chain().focus().undo().run()"
        :render-icon="renderToolbarIcon(UndoOutlined)"
        @click="editor.chain().focus().undo().run()"
      />
      <n-button
        :style="toolbarStyles"
        :size="toolbarSize"
        :disabled="!editor.can().chain().focus().redo().run()"
        :render-icon="renderToolbarIcon(RedoOutlined)"
        @click="editor.chain().focus().redo().run()"
      />
      <n-button
        :style="toolbarStyles"
        :size="toolbarSize"
        :render-icon="renderToolbarIcon(HtmlOutlined)"
        @click="showHtml = !showHtml"
      />
    </div>
    <editor-content :editor="editor" />
  </div>
</template>

<style scoped>
.toolbar {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-start;
  flex-wrap: wrap;
  align-items: center;
}

.toolbar * {
  font-weight: var(--app-ui-font-weight-bold) !important;
}
</style>
