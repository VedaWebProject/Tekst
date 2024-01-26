<script setup lang="ts">
import {
  NButton,
  NInput,
  NFormItem,
  type InputInst,
  type FormItemRule,
  NForm,
  type FormItemInst,
} from 'naive-ui';
import ButtonShelf from './ButtonShelf.vue';
import { ref } from 'vue';
import GenericModal from '@/components/generic/GenericModal.vue';
import { $t } from '@/i18n';
import { useMessages } from '@/composables/messages';

export interface PromptModalProps {
  actionKey?: string;
  initialValue?: string;
  inputLabel?: string;
  title?: string;
  multiline?: boolean;
  placeholder?: string;
  rows?: number;
  disableOkWhenNoValue?: boolean;
  validationRules?: FormItemRule[];
}

const props = withDefaults(defineProps<PromptModalProps>(), {
  actionKey: undefined,
  initialValue: undefined,
  inputLabel: undefined,
  title: undefined,
  multiline: false,
  placeholder: '',
  rows: undefined,
  disableOkWhenNoValue: false,
  validationRules: undefined,
});
const liveProps = ref<PromptModalProps>(props);
const emit = defineEmits(['submit', 'afterLeave']);
defineExpose({ open });

const show = ref(false);

const { message } = useMessages();
const inputRef = ref<InputInst>();
const formItemRef = ref<FormItemInst | null>(null);
const formModel = ref<{ inputString: string | undefined }>({ inputString: undefined });

function open(propsOverrides: PromptModalProps) {
  liveProps.value = { ...props, ...propsOverrides };
  formModel.value.inputString = liveProps.value.initialValue;
  show.value = true;
}

function close() {
  formModel.value.inputString = undefined;
  liveProps.value = props;
  show.value = false;
}

function handleSubmit() {
  formItemRef.value
    ?.validate()
    .then(() => {
      emit('submit', liveProps.value.actionKey, formModel.value.inputString);
      close();
    })
    .catch(() => {
      message.error($t('errors.followFormRules'));
    });
}

function handleInputReturn(e: KeyboardEvent) {
  if (!liveProps.value.multiline) {
    e.preventDefault();
    e.stopPropagation();
    handleSubmit();
  }
}
</script>

<template>
  <GenericModal
    v-model:show="show"
    :title="liveProps.title"
    @after-leave="
      () => {
        close();
        emit('afterLeave');
      }
    "
    @after-enter="inputRef?.select()"
  >
    <n-form :model="formModel">
      <n-form-item
        ref="formItemRef"
        path="inputString"
        :label="liveProps.inputLabel"
        :show-label="!!liveProps.inputLabel"
        :rule="liveProps.validationRules"
      >
        <n-input
          ref="inputRef"
          v-model:value="formModel.inputString"
          :type="liveProps.multiline ? 'textarea' : 'text'"
          :rows="liveProps.rows"
          :default-value="liveProps.initialValue"
          :placeholder="liveProps.placeholder"
          @keydown.enter="handleInputReturn"
        />
      </n-form-item>
    </n-form>
    <ButtonShelf top-gap>
      <n-button secondary @click="close">
        {{ $t('general.cancelAction') }}
      </n-button>
      <n-button
        type="primary"
        :disabled="liveProps.disableOkWhenNoValue && !formModel.inputString"
        @click="handleSubmit"
      >
        {{ $t('general.okAction') }}
      </n-button>
    </ButtonShelf>
  </GenericModal>
</template>
