<script setup lang="ts">
import { useFormRules } from '@/formRules';
import { useMessages } from '@/messages';
import type { TextUpdate } from '@/openapi';
import { useStateStore } from '@/stores';
import {
  NCheckbox,
  NSelect,
  NSpace,
  NButton,
  NForm,
  NFormItem,
  NInput,
  NColorPicker,
  type FormInst,
  useDialog,
} from 'naive-ui';
import { computed, ref, watch } from 'vue';
import { keepChangedRecords, haveRecordsChanged } from '@/utils';
import { useApi } from '@/api';
import { useI18n } from 'vue-i18n';

const state = useStateStore();
const dialog = useDialog();
const { message } = useMessages();
const { textFormRules } = useFormRules();
const { textsApi } = useApi();
const { t } = useI18n({ useScope: 'global' });
const loading = ref(false);

const initialModel = (): TextUpdate => ({
  title: state.text?.title,
  subtitle: state.text?.subtitle,
  slug: state.text?.slug,
  levels: state.text?.levels,
  defaultLevel: state.text?.defaultLevel,
  locDelim: state.text?.locDelim,
  labeledLocation: state.text?.labeledLocation,
  accentColor: state.text?.accentColor,
});
const model = ref<TextUpdate>(initialModel());
const modelChanged = computed(() => haveRecordsChanged(model.value, initialModel()));
const formRef = ref<FormInst | null>(null);
const defaultLevelOptions = computed(
  () =>
    model.value.levels?.map((l, i) => ({
      label: l,
      value: i,
    })) || []
);
watch(
  () => state.text,
  () => (model.value = initialModel())
);

function handleSave() {
  loading.value = true;
  formRef.value
    ?.validate((errors) => {
      if (!errors) {
        dialog.warning({
          title: t('general.warning'),
          content: t('admin.texts.general.msgRefreshWarn'),
          positiveText: t('general.saveAction'),
          negativeText: t('general.cancelAction'),
          style: 'font-weight: var(--app-ui-font-weight-light)',
          onPositiveClick: async () => {
            try {
              await textsApi.updateText({
                id: state.text?.id || '',
                textUpdate: keepChangedRecords(model.value, initialModel(), ['levels']),
              });
              location.reload();
            } catch {
              /**
               * This will be either an app-level error (e.g. buggy validation, server down, 401)
               * or the provided email already exists, which we don't want to actively disclose.
               */
              message.error(t('errors.unexpected'));
            } finally {
              loading.value = false;
            }
          },
          onNegativeClick: () => {
            loading.value = false;
          },
        });
      }
    })
    .catch(() => {
      message.error(t('errors.followFormRules'));
      loading.value = false;
    });
}
</script>

<template>
  <n-form
    ref="formRef"
    :model="model"
    :rules="textFormRules"
    label-placement="top"
    label-width="auto"
    require-mark-placement="right-hanging"
  >
    <n-form-item path="title" :label="$t('models.text.title')">
      <n-input
        v-model:value="model.title"
        type="text"
        :placeholder="$t('models.text.title')"
        @keydown.enter.prevent
        :disabled="loading"
      />
    </n-form-item>
    <n-form-item path="subtitle" :label="$t('models.text.subtitle')">
      <n-input
        v-model:value="model.subtitle"
        type="text"
        :placeholder="$t('models.text.subtitle')"
        @keydown.enter.prevent
        :disabled="loading"
      />
    </n-form-item>
    <n-form-item path="slug" :label="$t('models.text.slug')">
      <n-input
        v-model:value="model.slug"
        type="text"
        :placeholder="$t('models.text.slug')"
        @keydown.enter.prevent
        :disabled="loading"
      />
    </n-form-item>
    <n-form-item path="defaultLevel" :label="$t('models.text.defaultLevel')">
      <n-select
        v-model:value="model.defaultLevel"
        :options="defaultLevelOptions"
        :disabled="loading || !defaultLevelOptions.length"
        style="font-weight: var(--app-ui-font-weight-normal)"
      />
    </n-form-item>
    <n-form-item path="locDelim" :label="$t('models.text.locDelim')">
      <n-input
        v-model:value="model.locDelim"
        type="text"
        :placeholder="$t('models.text.locDelim')"
        @keydown.enter.prevent
        :disabled="loading"
      />
    </n-form-item>
    <n-form-item path="labeledLocation" :label="$t('models.text.labeledLocation')">
      <n-checkbox v-model:checked="model.labeledLocation" :disabled="loading">
        {{ $t('models.text.labeledLocation') }}
      </n-checkbox>
    </n-form-item>
    <n-form-item path="accentColor" :label="$t('models.text.accentColor')">
      <n-color-picker
        v-model:value="model.accentColor"
        :modes="['hex']"
        :show-alpha="false"
        :swatches="[
          '#305D97',
          '#097F86',
          '#43895F',
          '#D49101',
          '#D26E2B',
          '#D43A35',
          '#B83E63',
          '#88447F',
        ]"
      />
    </n-form-item>
  </n-form>
  <n-space :size="12" justify="end" style="margin-top: 0.5rem">
    <n-button
      secondary
      block
      @click="() => (model = initialModel())"
      :loading="loading"
      :disabled="loading || !modelChanged"
    >
      {{ $t('general.resetAction') }}
    </n-button>
    <n-button
      block
      type="primary"
      @click="handleSave"
      :loading="loading"
      :disabled="loading || !modelChanged"
    >
      {{ $t('general.saveAction') }}
    </n-button>
  </n-space>
</template>
