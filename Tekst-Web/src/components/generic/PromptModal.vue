<script setup lang="ts">
import { NButton, NInput, NFormItem, type InputInst } from 'naive-ui';
import ButtonShelf from './ButtonShelf.vue';
import { ref } from 'vue';
import GenericModal from '@/components/generic/GenericModal.vue';

export interface PromptModalProps {
  show?: boolean;
  actionKey?: string;
  initialValue?: string;
  inputLabel?: string;
  title?: string;
  multiline?: boolean;
  rows?: number;
  disableOkWhenNoValue?: boolean;
}

const props = defineProps<PromptModalProps>();
const emit = defineEmits(['update:show', 'submit', 'afterLeave']);

const inputRef = ref<InputInst>();
const value = ref<string>();

function handleSubmit() {
  emit('submit', props.actionKey, value.value);
  emit('update:show', false);
}

function handleInputReturn(e: KeyboardEvent) {
  if (!props.multiline) {
    e.preventDefault();
    e.stopPropagation();
    handleSubmit();
  }
}
</script>

<template>
  <GenericModal
    :show="show"
    :title="title"
    @update:show="emit('update:show', $event)"
    @after-leave="
      () => {
        value = undefined;
        emit('afterLeave');
      }
    "
    @after-enter="inputRef?.select()"
  >
    <n-form-item :label="inputLabel" :show-label="!!inputLabel">
      <n-input
        ref="inputRef"
        v-model:value="value"
        :type="multiline ? 'textarea' : 'text'"
        :rows="multiline && rows ? rows : multiline ? 3 : undefined"
        :default-value="initialValue"
        placeholder=""
        @keydown.enter="handleInputReturn"
      />
    </n-form-item>
    <ButtonShelf top-gap>
      <n-button secondary @click="emit('update:show', false)">
        {{ $t('general.cancelAction') }}
      </n-button>
      <n-button type="primary" :disabled="disableOkWhenNoValue && !value" @click="handleSubmit">
        {{ $t('general.okAction') }}
      </n-button>
    </ButtonShelf>
  </GenericModal>
</template>
