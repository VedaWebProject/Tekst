<script setup lang="ts">
import { useThemeStore } from '@/stores';
import { LanguageSupport } from '@codemirror/language';
import type { Extension } from '@codemirror/state';
import { dracula, tomorrow } from 'thememirror';
import { computed } from 'vue';
import { Codemirror } from 'vue-codemirror';

const props = defineProps<{
  language?: (config?: Record<string, unknown>) => LanguageSupport;
  indentSize?: number;
}>();

const model = defineModel<string | undefined>();
const emit = defineEmits(['input', 'focus', 'blur']);

const theme = useThemeStore();

const codeEditorExtensions = computed<Extension[]>(() => [
  ...(props.language ? [props.language()] : []),
  theme.dark ? dracula : tomorrow,
]);
</script>

<template>
  <codemirror
    class="code-editor text-small"
    v-model="model"
    :indent-with-tab="true"
    :tab-size="indentSize || 2"
    :extensions="codeEditorExtensions"
    :style="{
      width: '100%',
      maxHeight: '768px',
    }"
    @change="emit('input')"
    @focus="emit('focus')"
    @blur="emit('blur')"
    @keydown.enter.stop.prevent
  />
</template>

<style scoped>
.code-editor :deep(.cm-selectionBackground) {
  background: var(--text-color) !important;
}

.code-editor :deep(.cm-activeLine) {
  background: var(--main-bg-color) !important;
}

.code-editor :deep(.cm-content) {
  min-height: 100px !important;
}
</style>
