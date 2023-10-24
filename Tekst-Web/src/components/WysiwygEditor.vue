<script setup lang="ts">
import { computed, onUnmounted, h, type Component, type CSSProperties } from 'vue';
import { NSelect, NButton, NIcon, type SelectOption } from 'naive-ui';
import { useEditor, EditorContent } from '@tiptap/vue-3';
import StarterKit from '@tiptap/starter-kit';
import TextAlign from '@tiptap/extension-text-align';
import Link from '@tiptap/extension-link';
import Image from '@tiptap/extension-image';
import PromptModal from './PromptModal.vue';
import { PromptTemplatePromise } from '@/templatePromises';

import FormatBoldOutlined from '@vicons/material/FormatBoldOutlined';
import FormatItalicOutlined from '@vicons/material/FormatItalicOutlined';
import CodeOutlined from '@vicons/material/CodeOutlined';
import FormatClearOutlined from '@vicons/material/FormatClearOutlined';
import FormatQuoteFilled from '@vicons/material/FormatQuoteFilled';
import FormatListBulletedOutlined from '@vicons/material/FormatListBulletedOutlined';
import FormatListNumberedOutlined from '@vicons/material/FormatListNumberedOutlined';
import HorizontalRuleOutlined from '@vicons/material/HorizontalRuleOutlined';
import KeyboardReturnOutlined from '@vicons/material/KeyboardReturnOutlined';
import UndoOutlined from '@vicons/material/UndoOutlined';
import RedoOutlined from '@vicons/material/RedoOutlined';
import FormatAlignLeftOutlined from '@vicons/material/FormatAlignLeftOutlined';
import FormatAlignCenterOutlined from '@vicons/material/FormatAlignCenterOutlined';
import FormatAlignRightOutlined from '@vicons/material/FormatAlignRightOutlined';
import FormatAlignJustifyOutlined from '@vicons/material/FormatAlignJustifyOutlined';
import InsertLinkOutlined from '@vicons/material/InsertLinkOutlined';
import FormatSizeOutlined from '@vicons/material/FormatSizeOutlined';
import ShortTextOutlined from '@vicons/material/ShortTextOutlined';
import ImageOutlined from '@vicons/material/ImageOutlined';

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
const currentBlockType = computed(
  () =>
    (blockTypeOptions.find((o) => o.isActive() && o.value !== 'normal') || blockTypeOptions[0])
      .value
);

const editor = useEditor({
  content: props.document,
  extensions: [
    StarterKit.configure({
      heading: {
        levels: [1, 2, 3, 4],
      },
    }),
    TextAlign.configure({
      types: ['heading', 'paragraph'],
    }),
    Link.configure({
      openOnClick: false,
    }),
    Image.configure({
      inline: true,
      allowBase64: true,
    }),
  ],
  injectCSS: false,
  onUpdate: () => {
    emit('update:document', editor.value?.getHTML());
  },
  editorProps: {
    attributes: {
      style: 'outline: 0;',
    },
  },
});

const blockTypeOptions = [
  {
    label: 'Normal Text',
    value: 'normal',
    action: () => {
      editor.value?.commands.clearNodes();
      editor.value?.chain().focus().setParagraph().run();
    },
    isActive: () => editor.value?.isActive('paragraph'),
    iconComponent: ShortTextOutlined,
  },
  {
    label: 'Heading 1',
    value: 'h1',
    action: () => editor.value?.chain().focus().toggleHeading({ level: 1 }).run(),
    isActive: () => editor.value?.isActive('heading', { level: 1 }),
    iconComponent: FormatSizeOutlined,
  },
  {
    label: 'Heading 2',
    value: 'h2',
    action: () => editor.value?.chain().focus().toggleHeading({ level: 2 }).run(),
    isActive: () => editor.value?.isActive('heading', { level: 2 }),
    iconComponent: FormatSizeOutlined,
  },
  {
    label: 'Heading 3',
    value: 'h3',
    action: () => editor.value?.chain().focus().toggleHeading({ level: 3 }).run(),
    isActive: () => editor.value?.isActive('heading', { level: 3 }),
    iconComponent: FormatSizeOutlined,
  },
  {
    label: 'Heading 4',
    value: 'h4',
    action: () => editor.value?.chain().focus().toggleHeading({ level: 4 }).run(),
    isActive: () => editor.value?.isActive('heading', { level: 4 }),
    iconComponent: FormatSizeOutlined,
  },
  {
    label: 'Bulleted List',
    value: 'bulletedList',
    action: () => editor.value?.chain().focus().toggleBulletList().run(),
    isActive: () => editor.value?.isActive('bulletList'),
    iconComponent: FormatListBulletedOutlined,
  },
  {
    label: 'Numbered List',
    value: 'numberedList',
    action: () => editor.value?.chain().focus().toggleOrderedList().run(),
    isActive: () => editor.value?.isActive('orderedList'),
    iconComponent: FormatListNumberedOutlined,
  },
  {
    label: 'Blockquote',
    value: 'blockQuote',
    action: () => editor.value?.chain().focus().toggleBlockquote().run(),
    isActive: () => editor.value?.isActive('blockquote'),
    iconComponent: FormatQuoteFilled,
  },
  {
    label: 'Code Block',
    value: 'code',
    action: () => editor.value?.chain().focus().toggleCodeBlock().run(),
    isActive: () => editor.value?.isActive('codeBlock'),
    iconComponent: CodeOutlined,
  },
];

const toolbarStyles = computed<CSSProperties>(() => ({
  fontSize: { small: 18, medium: 22, large: 24 }[props.toolbarSize],
}));

function renderToolbarIcon(icon?: Component) {
  return () =>
    h(
      NIcon,
      { size: toolbarStyles.value.fontSize },
      {
        default: icon ? () => h(icon) : undefined,
      }
    );
}

function renderBlockTypeOption(option: SelectOption) {
  return [
    h(
      NIcon,
      {
        style: {
          verticalAlign: '-0.15em',
          marginRight: '4px',
        },
      },
      {
        default: () => h(option.iconComponent as Component),
      }
    ),
    option.label as string,
  ];
}

async function handleAddLinkClick() {
  try {
    const url = await PromptTemplatePromise.start(
      'Link',
      'Set Link URL:',
      editor.value?.getAttributes('link').href
    );
    // empty
    if (url === '') {
      if (editor.value?.isActive('link')) {
        editor.value?.chain().focus().unsetLink().run();
      } else {
        editor.value?.chain().focus().extendMarkRange('link').unsetLink().run();
      }
      return;
    }
    // update link
    editor.value?.chain().focus().extendMarkRange('link').setLink({ href: url }).run();
  } catch {
    return;
  }
}

async function handleAddImageClick() {
  try {
    const url = await PromptTemplatePromise.start('Image', 'Set Image URL:', undefined);
    // empty
    if (url === '') return;
    // update link
    editor.value?.chain().focus().setImage({ src: url }).run();
  } catch {
    return;
  }
}

function handleSelectBlockType(value: string, option: SelectOption) {
  (option.action as () => void)();
}

onUnmounted(() => {
  editor.value?.destroy();
});
</script>

<template>
  <div>
    <div v-if="editor" class="toolbar">
      <n-select
        :value="currentBlockType"
        :options="blockTypeOptions"
        :size="toolbarSize"
        :consistent-menu-width="false"
        :render-label="renderBlockTypeOption"
        style="width: auto; flex-grow: 2"
        @update:value="handleSelectBlockType"
      />
      <div class="spacer"></div>
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
        :type="(editor.isActive('italic') && 'primary') || undefined"
        :render-icon="renderToolbarIcon(FormatItalicOutlined)"
        @click="editor.chain().focus().toggleItalic().run()"
      />
      <div class="spacer"></div>
      <n-button
        :style="toolbarStyles"
        :size="toolbarSize"
        :type="(editor.isActive('link') && 'primary') || undefined"
        :render-icon="renderToolbarIcon(InsertLinkOutlined)"
        @click="handleAddLinkClick"
      />
      <n-button
        :style="toolbarStyles"
        :size="toolbarSize"
        :disabled="!editor.can().chain().focus().toggleCode().run()"
        :type="(editor.isActive('code') && 'primary') || undefined"
        :render-icon="renderToolbarIcon(CodeOutlined)"
        @click="editor.chain().focus().toggleCode().run()"
      />
      <div class="spacer"></div>
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
      <div class="spacer"></div>
      <n-button
        :style="toolbarStyles"
        :size="toolbarSize"
        :render-icon="renderToolbarIcon(FormatAlignLeftOutlined)"
        :type="(editor.isActive({ textAlign: 'left' }) && 'primary') || undefined"
        @click="editor.chain().focus().setTextAlign('left').run()"
      />
      <n-button
        :style="toolbarStyles"
        :size="toolbarSize"
        :render-icon="renderToolbarIcon(FormatAlignCenterOutlined)"
        :type="(editor.isActive({ textAlign: 'center' }) && 'primary') || undefined"
        @click="editor.chain().focus().setTextAlign('center').run()"
      />
      <n-button
        :style="toolbarStyles"
        :size="toolbarSize"
        :render-icon="renderToolbarIcon(FormatAlignRightOutlined)"
        :type="(editor.isActive({ textAlign: 'right' }) && 'primary') || undefined"
        @click="editor.chain().focus().setTextAlign('right').run()"
      />
      <n-button
        :style="toolbarStyles"
        :size="toolbarSize"
        :render-icon="renderToolbarIcon(FormatAlignJustifyOutlined)"
        :type="(editor.isActive({ textAlign: 'justify' }) && 'primary') || undefined"
        @click="editor.chain().focus().setTextAlign('justify').run()"
      />
      <div class="spacer"></div>
      <n-button
        :style="toolbarStyles"
        :size="toolbarSize"
        :render-icon="renderToolbarIcon(HorizontalRuleOutlined)"
        @click="editor.chain().focus().setHorizontalRule().run()"
      />
      <n-button
        :style="toolbarStyles"
        :size="toolbarSize"
        :render-icon="renderToolbarIcon(ImageOutlined)"
        @click="handleAddImageClick"
      />
      <n-button
        :style="toolbarStyles"
        :size="toolbarSize"
        :render-icon="renderToolbarIcon(KeyboardReturnOutlined)"
        @click="editor.chain().focus().setHardBreak().run()"
      />
      <div class="spacer"></div>
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
    </div>
    <div
      style="
        margin: 0.5rem 0;
        padding: 4px var(--content-gap);
        border: 1px solid var(--text-color);
        border-radius: var(--app-ui-border-radius);
        max-height: 50vh;
        overflow-y: scroll;
      "
    >
      <editor-content :editor="editor" />
    </div>
  </div>
  <PromptModal />
</template>

<style scoped>
.toolbar {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-start;
  flex-wrap: wrap;
  align-items: flex-end;
}

.toolbar * {
  font-weight: var(--app-ui-font-weight-bold) !important;
}

.toolbar > .spacer {
  margin: 0 2px;
}
</style>
