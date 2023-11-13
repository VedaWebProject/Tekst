<script setup lang="ts">
import { $t } from '@/i18n';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import { ref } from 'vue';
import { NButton, NSelect, NForm, NFormItem, NInput, type FormInst, useDialog } from 'naive-ui';
import { usePlatformData } from '@/platformData';
import { PATCH, type PlatformSettingsUpdate } from '@/api';

import { useModelChanges } from '@/modelChanges';
import { useMessages } from '@/messages';
import { platformSettingsFormRules } from '@/formRules';

import { negativeButtonProps, positiveButtonProps } from '@/components/dialogButtonProps';

const { pfData, loadPlatformData } = usePlatformData();
const { message } = useMessages();
const dialog = useDialog();

const getFormModel = (): PlatformSettingsUpdate => ({
  defaultTextId: pfData.value?.settings.defaultTextId,
  infoPlatformName: pfData.value?.settings.infoPlatformName,
});

const loading = ref(false);
const formRef = ref<FormInst | null>(null);
const formModel = ref<PlatformSettingsUpdate>(getFormModel());

const { changed, reset, getChanges } = useModelChanges(formModel);

const defaultTextOptions = pfData.value?.texts.map((t) => ({
  label: t.title,
  value: t.id,
}));

async function handleSaveClick() {
  loading.value = true;
  formRef.value
    ?.validate(async (validationError) => {
      if (validationError) return;
      const { error } = await PATCH('/platform/settings', {
        body: getChanges(),
      });
      if (!error) {
        await loadPlatformData();
        message.success($t('admin.system.platformSettings.msgSaved'));
      } else {
        message.error($t('errors.unexpected'));
      }
      reset();
      loading.value = false;
    })
    .catch(() => {
      message.error($t('errors.followFormRules'));
      reset();
      loading.value = false;
    });
}

function handleResetClick() {
  if (!changed) {
    resetForm();
    return;
  }
  dialog.warning({
    title: $t('general.warning'),
    content: $t('admin.system.segments.warnCancel'),
    positiveText: $t('general.yesAction'),
    negativeText: $t('general.noAction'),
    positiveButtonProps: positiveButtonProps,
    negativeButtonProps: negativeButtonProps,
    autoFocus: false,
    closable: false,
    onPositiveClick: resetForm,
  });
}

function resetForm() {
  formModel.value = getFormModel();
  reset();
  formRef.value?.restoreValidation();
}
</script>

<template>
  <h2>
    {{ $t('admin.system.platformSettings.heading') }}
    <HelpButtonWidget help-key="adminSystemSettingsView" />
  </h2>

  <div class="content-block">
    <n-form
      ref="formRef"
      :model="formModel"
      :rules="platformSettingsFormRules"
      label-placement="top"
      label-width="auto"
      require-mark-placement="right-hanging"
    >
      <!-- PLATFORM TITLE -->
      <n-form-item
        path="infoPlatformName"
        :label="$t('models.platformSettings.infoPlatformName')"
        required
      >
        <n-input
          v-model:value="formModel.infoPlatformName"
          type="text"
          :placeholder="$t('models.platformSettings.infoPlatformName')"
          :disabled="loading"
          @keydown.enter.prevent
        />
      </n-form-item>
      <!-- DEFAULT TEXT -->
      <n-form-item :label="$t('models.platformSettings.defaultText')">
        <n-select
          v-model:value="formModel.defaultTextId"
          :options="defaultTextOptions"
          :placeholder="$t('models.platformSettings.defaultText')"
          :consistent-menu-width="false"
          style="min-width: 200px"
          @keydown.enter.prevent
        />
      </n-form-item>
    </n-form>

    <div style="display: flex; gap: var(--layout-gap); justify-content: end">
      <n-button secondary @click="handleResetClick">{{ $t('general.resetAction') }}</n-button>
      <n-button type="primary" :disabled="!changed" @click="handleSaveClick">{{
        $t('general.saveAction')
      }}</n-button>
    </div>
  </div>
</template>
