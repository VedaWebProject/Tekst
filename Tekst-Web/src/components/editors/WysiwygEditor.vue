<script setup lang="ts">
import { computed, onUnmounted, h, type Component, type CSSProperties, watch, ref } from 'vue';
import { NSelect, NButton, NIcon, type SelectOption } from 'naive-ui';
import { useEditor, EditorContent } from '@tiptap/vue-3';
import StarterKit from '@tiptap/starter-kit';
import TextAlign from '@tiptap/extension-text-align';
import CharacterCount from '@tiptap/extension-character-count';
import Link from '@tiptap/extension-link';
import Image from '@tiptap/extension-image';
import PromptModal from '@/components/generic/PromptModal.vue';
import { $t } from '@/i18n';

import {
  FormatBoldIcon,
  FormatItalicIcon,
  CodeIcon,
  FormatClearIcon,
  FormatQuoteIcon,
  FormatListBulletedIcon,
  FormatListNumberedIcon,
  HorizontalRuleIcon,
  KeyboardReturnIcon,
  UndoIcon,
  RedoIcon,
  FormatAlignLeftIcon,
  FormatAlignCenterIcon,
  FormatAlignRightIcon,
  FormatAlignJustifyIcon,
  LinkIcon,
  FormatSizeIcon,
  ShortTextIcon,
  ImageIcon,
} from '@/icons';
import { wysiwygEditorFormRules } from '@/forms/formRules';

const props = withDefaults(
  defineProps<{
    value?: string | null;
    toolbarSize?: 'small' | 'medium' | 'large';
    maxChars?: number;
  }>(),
  {
    value: '',
    toolbarSize: 'small',
    maxChars: undefined,
  }
);

const emit = defineEmits(['update:value', 'blur', 'focus', 'input']);

const promptModalRef = ref();

watch(
  () => props.value,
  (newDocument) => {
    if (newDocument !== editor.value?.getHTML()) {
      editor.value?.commands.setContent(props.value);
    }
  }
);

const editor = useEditor({
  content: props.value,
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
    CharacterCount.configure({
      limit: props.maxChars,
      mode: 'textSize',
    }),
  ],
  injectCSS: false,
  onUpdate: () => {
    emit('update:value', editor.value?.getHTML());
  },
  onBlur: () => {
    emit('blur');
  },
  onFocus: () => {
    emit('focus');
  },
  onTransaction: () => {
    emit('input');
  },
  editorProps: {
    attributes: {
      style: 'outline: 0;',
    },
  },
});

const blockTypeOptions = computed(() => [
  {
    label: $t('wysiwyg.blockTypes.paragraph'),
    value: 'normal',
    action: () => {
      editor.value?.commands.clearNodes();
      editor.value?.chain().focus().setParagraph().run();
    },
    isActive: () => editor.value?.isActive('paragraph'),
    iconComponent: ShortTextIcon,
  },
  {
    label: $t('wysiwyg.blockTypes.heading', { level: 1 }),
    value: 'h1',
    action: () => editor.value?.chain().focus().toggleHeading({ level: 1 }).run(),
    isActive: () => editor.value?.isActive('heading', { level: 1 }),
    iconComponent: FormatSizeIcon,
  },
  {
    label: $t('wysiwyg.blockTypes.heading', { level: 2 }),
    value: 'h2',
    action: () => editor.value?.chain().focus().toggleHeading({ level: 2 }).run(),
    isActive: () => editor.value?.isActive('heading', { level: 2 }),
    iconComponent: FormatSizeIcon,
  },
  {
    label: $t('wysiwyg.blockTypes.heading', { level: 3 }),
    value: 'h3',
    action: () => editor.value?.chain().focus().toggleHeading({ level: 3 }).run(),
    isActive: () => editor.value?.isActive('heading', { level: 3 }),
    iconComponent: FormatSizeIcon,
  },
  {
    label: $t('wysiwyg.blockTypes.heading', { level: 4 }),
    value: 'h4',
    action: () => editor.value?.chain().focus().toggleHeading({ level: 4 }).run(),
    isActive: () => editor.value?.isActive('heading', { level: 4 }),
    iconComponent: FormatSizeIcon,
  },
  {
    label: $t('wysiwyg.blockTypes.bulletedList'),
    value: 'bulletedList',
    action: () => editor.value?.chain().focus().toggleBulletList().run(),
    isActive: () => editor.value?.isActive('bulletList'),
    iconComponent: FormatListBulletedIcon,
  },
  {
    label: $t('wysiwyg.blockTypes.numberedList'),
    value: 'numberedList',
    action: () => editor.value?.chain().focus().toggleOrderedList().run(),
    isActive: () => editor.value?.isActive('orderedList'),
    iconComponent: FormatListNumberedIcon,
  },
  {
    label: $t('wysiwyg.blockTypes.blockQuote'),
    value: 'blockQuote',
    action: () => editor.value?.chain().focus().toggleBlockquote().run(),
    isActive: () => editor.value?.isActive('blockquote'),
    iconComponent: FormatQuoteIcon,
  },
  {
    label: $t('wysiwyg.blockTypes.codeBlock'),
    value: 'code',
    action: () => editor.value?.chain().focus().toggleCodeBlock().run(),
    isActive: () => editor.value?.isActive('codeBlock'),
    iconComponent: CodeIcon,
  },
]);

const currentBlockType = computed(
  () =>
    (
      blockTypeOptions.value.find((o) => o.isActive() && o.value !== 'normal') ||
      blockTypeOptions.value[0]
    ).value
);

const toolbarStyles = computed<CSSProperties>(() => ({
  fontSize: { small: 18, medium: 22, large: 24 }[props.toolbarSize],
}));

function renderToolbarIcon(icon?: Component) {
  return () =>
    h(NIcon, null, {
      default: icon ? () => h(icon) : undefined,
    });
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

function handleAddLinkClick() {
  promptModalRef.value.open({
    actionKey: 'addLink',
    initialValue: editor.value?.getAttributes('link').href,
    title: $t('wysiwyg.linkPrompt.title'),
    inputLabel: $t('wysiwyg.linkPrompt.inputLabel'),
    validationRules: wysiwygEditorFormRules.linkUrl,
  });
}

async function handleAddImageClick() {
  promptModalRef.value.open({
    actionKey: 'addImage',
    title: $t('wysiwyg.imagePrompt.title'),
    inputLabel: $t('wysiwyg.imagePrompt.inputLabel'),
    disableOkWhenNoValue: true,
    validationRules: wysiwygEditorFormRules.imageUrl,
  });
}

async function handlePromptModalSubmit(actionKey: string, value: string) {
  if (actionKey === 'addLink') {
    // empty
    if (value) {
      // update link
      editor.value?.chain().focus().extendMarkRange('link').setLink({ href: value }).run();
    } else {
      if (editor.value?.isActive('link')) {
        editor.value?.chain().focus().unsetLink().run();
      } else {
        editor.value?.chain().focus().extendMarkRange('link').unsetLink().run();
      }
    }
  } else if (actionKey === 'addImage') {
    // empty
    if (!value) return;
    // update link
    editor.value?.chain().focus().setImage({ src: value }).run();
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
  <div v-if="editor" style="width: 100%">
    <div class="toolbar">
      <n-select
        :value="currentBlockType"
        :options="blockTypeOptions"
        :size="toolbarSize"
        :consistent-menu-width="false"
        status="success"
        :render-label="renderBlockTypeOption"
        style="width: auto; min-width: 320px; flex-grow: 2"
        @update:value="handleSelectBlockType"
      />
      <div class="toolbar-group">
        <n-button
          :style="toolbarStyles"
          :size="toolbarSize"
          :title="$t('wysiwyg.bold')"
          :disabled="!editor.can().chain().focus().toggleBold().run()"
          :type="(editor.isActive('bold') && 'primary') || undefined"
          :render-icon="renderToolbarIcon(FormatBoldIcon)"
          :focusable="false"
          @click="editor.chain().focus().toggleBold().run()"
        />
        <n-button
          :style="toolbarStyles"
          :size="toolbarSize"
          :title="$t('wysiwyg.italic')"
          :disabled="!editor.can().chain().focus().toggleItalic().run()"
          :type="(editor.isActive('italic') && 'primary') || undefined"
          :render-icon="renderToolbarIcon(FormatItalicIcon)"
          :focusable="false"
          @click="editor.chain().focus().toggleItalic().run()"
        />
      </div>
      <div class="toolbar-group">
        <n-button
          :style="toolbarStyles"
          :size="toolbarSize"
          :title="$t('wysiwyg.link')"
          :type="(editor.isActive('link') && 'primary') || undefined"
          :render-icon="renderToolbarIcon(LinkIcon)"
          :focusable="false"
          @click="handleAddLinkClick"
        />
        <n-button
          :style="toolbarStyles"
          :size="toolbarSize"
          :title="$t('wysiwyg.inlineCode')"
          :disabled="!editor.can().chain().focus().toggleCode().run()"
          :type="(editor.isActive('code') && 'primary') || undefined"
          :render-icon="renderToolbarIcon(CodeIcon)"
          :focusable="false"
          @click="editor.chain().focus().toggleCode().run()"
        />
      </div>
      <div class="toolbar-group">
        <n-button
          :style="toolbarStyles"
          :size="toolbarSize"
          :title="$t('wysiwyg.clearFormat')"
          :render-icon="renderToolbarIcon(FormatClearIcon)"
          :focusable="false"
          @click="
            () => {
              editor?.chain().focus().unsetAllMarks().run();
              editor?.chain().focus().clearNodes().run();
            }
          "
        />
      </div>
      <div class="toolbar-group">
        <n-button
          :style="toolbarStyles"
          :size="toolbarSize"
          :title="$t('wysiwyg.alignLeft')"
          :render-icon="renderToolbarIcon(FormatAlignLeftIcon)"
          :type="(editor.isActive({ textAlign: 'left' }) && 'primary') || undefined"
          :focusable="false"
          @click="editor.chain().focus().setTextAlign('left').run()"
        />
        <n-button
          :style="toolbarStyles"
          :size="toolbarSize"
          :title="$t('wysiwyg.alignCenter')"
          :render-icon="renderToolbarIcon(FormatAlignCenterIcon)"
          :type="(editor.isActive({ textAlign: 'center' }) && 'primary') || undefined"
          :focusable="false"
          @click="editor.chain().focus().setTextAlign('center').run()"
        />
        <n-button
          :style="toolbarStyles"
          :size="toolbarSize"
          :title="$t('wysiwyg.alignRight')"
          :render-icon="renderToolbarIcon(FormatAlignRightIcon)"
          :type="(editor.isActive({ textAlign: 'right' }) && 'primary') || undefined"
          :focusable="false"
          @click="editor.chain().focus().setTextAlign('right').run()"
        />
        <n-button
          :style="toolbarStyles"
          :size="toolbarSize"
          :title="$t('wysiwyg.alignJustify')"
          :render-icon="renderToolbarIcon(FormatAlignJustifyIcon)"
          :type="(editor.isActive({ textAlign: 'justify' }) && 'primary') || undefined"
          :focusable="false"
          @click="editor.chain().focus().setTextAlign('justify').run()"
        />
      </div>
      <div class="toolbar-group">
        <n-button
          :style="toolbarStyles"
          :size="toolbarSize"
          :title="$t('wysiwyg.horizontalRule')"
          :render-icon="renderToolbarIcon(HorizontalRuleIcon)"
          :focusable="false"
          @click="editor.chain().focus().setHorizontalRule().run()"
        />
        <n-button
          :style="toolbarStyles"
          :size="toolbarSize"
          :title="$t('wysiwyg.image')"
          :render-icon="renderToolbarIcon(ImageIcon)"
          :focusable="false"
          @click="handleAddImageClick"
        />
        <n-button
          :style="toolbarStyles"
          :size="toolbarSize"
          :title="$t('wysiwyg.hardBreak')"
          :render-icon="renderToolbarIcon(KeyboardReturnIcon)"
          :focusable="false"
          @click="editor.chain().focus().setHardBreak().run()"
        />
      </div>
      <div class="toolbar-group">
        <n-button
          :style="toolbarStyles"
          :size="toolbarSize"
          :title="$t('wysiwyg.undo')"
          :disabled="!editor.can().chain().focus().undo().run()"
          :render-icon="renderToolbarIcon(UndoIcon)"
          :focusable="false"
          @click="editor.chain().focus().undo().run()"
        />
        <n-button
          :style="toolbarStyles"
          :size="toolbarSize"
          :title="$t('wysiwyg.redo')"
          :disabled="!editor.can().chain().focus().redo().run()"
          :render-icon="renderToolbarIcon(RedoIcon)"
          :focusable="false"
          @click="editor.chain().focus().redo().run()"
        />
      </div>
    </div>
    <div
      style="
        margin: 0.5rem 0;
        padding: 4px var(--content-gap);
        border: 1px solid var(--text-color-fade);
        border-radius: var(--app-ui-border-radius);
        max-height: 50vh;
        overflow-y: scroll;
      "
    >
      <editor-content :editor="editor" />
    </div>
    <div v-if="editor" class="character-count">{{ editor.getHTML().length }} / {{ maxChars }}</div>
  </div>
  <PromptModal ref="promptModalRef" @submit="handlePromptModalSubmit" />
</template>

<style scoped>
.toolbar {
  display: flex;
  gap: 1rem;
  justify-content: flex-start;
  flex-wrap: wrap;
  align-items: flex-end;
}

.toolbar * {
  font-weight: var(--app-ui-font-weight-bold) !important;
}

.toolbar > .toolbar-group {
  display: flex;
  flex-wrap: nowrap;
  gap: 0.4rem;
}

.character-count {
  text-align: right;
  font-size: var(--app-ui-font-size-tiny);
  color: var(--text-color-fade);
}
</style>
