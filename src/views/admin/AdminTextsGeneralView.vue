<script setup lang="ts">
import { useFormRules } from '@/formRules';
import { useMessages } from '@/messages';
import type { TextUpdate } from '@/openapi';
import { useStateStore } from '@/stores';
import { NSpace, NButton, NForm, NFormItem, NInput, NColorPicker, type FormInst } from 'naive-ui';
import { ref, watch } from 'vue';

const state = useStateStore();
const { message } = useMessages();
const formRules = useFormRules();
const loading = ref(false);

const initialFormModel = (): TextUpdate => ({
  title: state.text?.title,
  subtitle: state.text?.subtitle,
  slug: state.text?.slug,
  levels: state.text?.levels,
  defaultLevel: state.text?.defaultLevel,
  locDelim: state.text?.locDelim,
  labeledLocation: state.text?.labeledLocation,
  accentColor: state.text?.accentColor,
});
const formModel = ref<TextUpdate>(initialFormModel());
const formRef = ref<FormInst | null>(null);
watch(
  () => state.text,
  () => (formModel.value = initialFormModel())
);

function handleSave() {
  message.info('NOT IMPLEMENTED!');
}
</script>

<template>
  <n-form
    ref="formRef"
    :model="formModel"
    :rules="formRules"
    label-placement="top"
    label-width="auto"
    require-mark-placement="right-hanging"
  >
    <n-form-item path="title" :label="$t('models.text.title')">
      <n-input
        v-model:value="formModel.title"
        type="text"
        :placeholder="$t('models.text.title')"
        @keydown.enter.prevent
        :disabled="loading"
      />
    </n-form-item>
    <n-form-item path="subtitle" :label="$t('models.text.subtitle')">
      <n-input
        v-model:value="formModel.subtitle"
        type="text"
        :placeholder="$t('models.text.subtitle')"
        @keydown.enter.prevent
        :disabled="loading"
      />
    </n-form-item>
    <n-form-item path="slug" :label="$t('models.text.slug')">
      <n-input
        v-model:value="formModel.slug"
        type="text"
        :placeholder="$t('models.text.slug')"
        @keydown.enter.prevent
        :disabled="loading"
      />
    </n-form-item>
    <n-form-item path="accentColor" :label="$t('models.text.accentColor')">
      <n-color-picker
        v-model:value="formModel.accentColor"
        :modes="['hex']"
        :show-alpha="false"
        :swatches="['#FFFFFF', '#18A058', '#2080F0', '#F0A020']"
      />
    </n-form-item>
  </n-form>
  <n-space :size="12" justify="end">
    <n-button block type="primary" @click="handleSave" :loading="loading" :disabled="loading">
      {{ $t('general.saveAction') }}
    </n-button>
  </n-space>
</template>
