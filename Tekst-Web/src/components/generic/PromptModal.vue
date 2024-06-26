<script setup lang="ts">
import {
  NButton,
  NInput,
  NAlert,
  NFormItem,
  type InputInst,
  type FormItemRule,
  NForm,
  type FormItemInst,
} from 'naive-ui';
import ButtonShelf from './ButtonShelf.vue';
import { ref, type Component } from 'vue';
import GenericModal from '@/components/generic/GenericModal.vue';
import { $t } from '@/i18n';
import { useMessages } from '@/composables/messages';
import NInputOsk from '@/components/NInputOsk.vue';
import { shallowRef } from 'vue';

export interface PromptModalProps {
  actionKey?: string;
  initialValue?: string;
  msg?: string;
  icon?: Component;
  inputLabel?: string;
  title?: string;
  multiline?: boolean;
  osk?: boolean;
  font?: string;
  placeholder?: string;
  rows?: number;
  disableOkWhenNoValue?: boolean;
  validationRules?: FormItemRule[];
}

const props = withDefaults(defineProps<PromptModalProps>(), {
  actionKey: undefined,
  initialValue: undefined,
  msg: undefined,
  icon: undefined,
  inputLabel: undefined,
  title: undefined,
  multiline: false,
  osk: false,
  font: undefined,
  placeholder: '',
  rows: undefined,
  disableOkWhenNoValue: false,
  validationRules: undefined,
});
const liveProps = shallowRef<PromptModalProps>(props);
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
  <generic-modal
    v-model:show="show"
    :title="liveProps.title"
    :icon="liveProps.icon"
    @after-leave="
      () => {
        close();
        emit('afterLeave');
      }
    "
    @after-enter="inputRef?.select()"
  >
    <n-alert v-if="liveProps.msg" :show-icon="false" style="margin-bottom: var(--layout-gap)">
      <span class="text-medium">{{ liveProps.msg }}</span>
    </n-alert>
    <n-form :model="formModel">
      <n-form-item
        ref="formItemRef"
        path="inputString"
        :label="liveProps.inputLabel"
        :show-label="!!liveProps.inputLabel"
        :rule="liveProps.validationRules"
      >
        <n-input
          v-if="!liveProps.osk"
          ref="inputRef"
          v-model:value="formModel.inputString"
          :type="liveProps.multiline ? 'textarea' : 'text'"
          :rows="liveProps.rows"
          :default-value="liveProps.initialValue"
          :placeholder="liveProps.placeholder"
          @keydown.enter="handleInputReturn"
        />
        <n-input-osk
          v-else
          ref="inputRef"
          v-model:value="formModel.inputString"
          :type="liveProps.multiline ? 'textarea' : 'text'"
          :rows="liveProps.rows"
          :default-value="liveProps.initialValue"
          :placeholder="liveProps.placeholder"
          :font="liveProps.font"
          @keydown.enter="handleInputReturn"
        />
      </n-form-item>
    </n-form>
    <button-shelf top-gap>
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
    </button-shelf>
  </generic-modal>
</template>
