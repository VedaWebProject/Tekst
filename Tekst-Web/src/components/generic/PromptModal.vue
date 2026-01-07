<script setup lang="ts">
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import GenericModal from '@/components/generic/GenericModal.vue';
import OskInput from '@/components/OskInput.vue';
import { useMessages } from '@/composables/messages';
import { $t } from '@/i18n';
import {
  NAlert,
  NButton,
  NForm,
  NFormItem,
  NInput,
  NSelect,
  type FormItemInst,
  type FormItemRule,
  type InputInst,
} from 'naive-ui';
import { ref, shallowRef, type Component } from 'vue';

export interface PromptModalProps {
  actionKey?: string;
  initialValue?: string;
  type?: 'input' | 'input-osk' | 'textarea' | 'textarea-osk' | 'select';
  msg?: string;
  icon?: Component;
  inputLabel?: string;
  selectOptions?: { label: string; value: string }[];
  title?: string;
  font?: string;
  oskModeKey?: string;
  placeholder?: string;
  rows?: number;
  disableOkWhenNoValue?: boolean;
  validationRules?: FormItemRule[];
}

const props = withDefaults(defineProps<PromptModalProps>(), {
  type: 'input',
  multiline: false,
  disableOkWhenNoValue: false,
});
const liveProps = shallowRef<PromptModalProps>(props);
const emit = defineEmits(['submit', 'afterLeave']);
defineExpose({ open });

const show = ref(false);

const { message } = useMessages();
const inputRef = ref<InputInst>();
const formItemRef = ref<FormItemInst | null>(null);
const formModel = ref<{ input: string | undefined }>({ input: undefined });

function open(propsOverrides: PromptModalProps) {
  liveProps.value = { ...props, ...propsOverrides };
  formModel.value.input = liveProps.value.initialValue;
  show.value = true;
}

function close() {
  formModel.value.input = undefined;
  liveProps.value = props;
  show.value = false;
}

function handleSubmit() {
  formItemRef.value
    ?.validate()
    .then(() => {
      emit('submit', liveProps.value.actionKey, formModel.value.input);
      close();
    })
    .catch(() => {
      message.error($t('errors.followFormRules'));
    });
}

function handleInputReturn() {
  if (liveProps.value.type !== 'textarea' && liveProps.value.type === 'textarea-osk') {
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
    <n-alert v-if="liveProps.msg" :show-icon="false" class="mb-lg">
      <span class="text-medium">{{ liveProps.msg }}</span>
    </n-alert>
    <n-form :model="formModel">
      <n-form-item
        ref="formItemRef"
        path="input"
        :label="liveProps.inputLabel"
        :show-label="!!liveProps.inputLabel"
        :rule="liveProps.validationRules"
      >
        <n-input
          v-if="liveProps.type === 'input' || liveProps.type === 'textarea'"
          ref="inputRef"
          v-model:value="formModel.input"
          :type="liveProps.type === 'input' ? 'text' : 'textarea'"
          :rows="liveProps.rows"
          :default-value="liveProps.initialValue"
          :placeholder="liveProps.placeholder"
          @keydown.enter="handleInputReturn"
        />
        <osk-input
          v-else-if="liveProps.type === 'input-osk' || liveProps.type === 'textarea-osk'"
          ref="inputRef"
          v-model:value="formModel.input"
          :type="liveProps.type === 'input-osk' ? 'text' : 'textarea'"
          :rows="liveProps.rows"
          :default-value="liveProps.initialValue"
          :placeholder="liveProps.placeholder"
          :font="liveProps.font"
          :osk-key="liveProps.oskModeKey"
          @keydown.enter="handleInputReturn"
        />
        <n-select
          v-else-if="liveProps.type === 'select'"
          ref="inputRef"
          v-model:value="formModel.input"
          :options="liveProps.selectOptions"
          :default-value="liveProps.selectOptions?.[0]?.value"
        />
      </n-form-item>
    </n-form>
    <button-shelf top-gap>
      <n-button secondary @click="close">
        {{ $t('common.cancel') }}
      </n-button>
      <n-button
        type="primary"
        :disabled="liveProps.disableOkWhenNoValue && !formModel.input"
        @click="handleSubmit"
      >
        {{ $t('common.ok') }}
      </n-button>
    </button-shelf>
  </generic-modal>
</template>
