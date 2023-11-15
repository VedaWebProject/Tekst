<script setup lang="ts">
import { $t } from '@/i18n';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import { ref } from 'vue';
import { NCheckbox, NButton, NSelect, NForm, NFormItem, NInput, type FormInst } from 'naive-ui';
import { usePlatformData } from '@/platformData';
import { PATCH, type PlatformSettingsUpdate } from '@/api';

import { useModelChanges } from '@/modelChanges';
import { useMessages } from '@/messages';
import { platformSettingsFormRules } from '@/formRules';

const { pfData, patchPfData } = usePlatformData();
const { message } = useMessages();

const getFormModel = (): PlatformSettingsUpdate => Object.assign({}, pfData.value?.settings || {});

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
      const { data, error } = await PATCH('/platform/settings', {
        body: getChanges(),
      });
      if (!error) {
        patchPfData({
          settings: data,
        });
        message.success($t('admin.system.platformSettings.msgSaved'), undefined, 10);
      } else {
        message.error($t('errors.unexpected'), error);
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

  <n-form
    ref="formRef"
    :model="formModel"
    :rules="platformSettingsFormRules"
    label-placement="top"
    label-width="auto"
    require-mark-placement="right-hanging"
  >
    <div class="content-block">
      <h3>{{ $t('admin.system.platformSettings.headingInfo') }}</h3>

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
      <!-- PLATFORM DESCRIPTION -->
      <n-form-item path="infoDescription" :label="$t('models.platformSettings.infoDescription')">
        <n-input
          v-model:value="formModel.infoDescription"
          type="text"
          :placeholder="$t('models.platformSettings.infoDescription')"
          :disabled="loading"
          @keydown.enter.prevent
        />
      </n-form-item>
      <!-- TERMS URL -->
      <n-form-item path="infoTerms" :label="$t('models.platformSettings.infoTerms')">
        <n-input
          v-model:value="formModel.infoTerms"
          type="text"
          :placeholder="$t('models.platformSettings.infoTerms')"
          :disabled="loading"
          @keydown.enter.prevent
        />
      </n-form-item>
      <!-- CONTACT NAME -->
      <n-form-item path="infoContactName" :label="$t('models.platformSettings.infoContactName')">
        <n-input
          v-model:value="formModel.infoContactName"
          type="text"
          :placeholder="$t('models.platformSettings.infoContactName')"
          :disabled="loading"
          @keydown.enter.prevent
        />
      </n-form-item>
      <!-- CONTACT EMAIL -->
      <n-form-item path="infoContactEmail" :label="$t('models.platformSettings.infoContactEmail')">
        <n-input
          v-model:value="formModel.infoContactEmail"
          type="text"
          :placeholder="$t('models.platformSettings.infoContactEmail')"
          :disabled="loading"
          @keydown.enter.prevent
        />
      </n-form-item>
      <!-- CONTACT URL -->
      <n-form-item path="infoContactUrl" :label="$t('models.platformSettings.infoContactUrl')">
        <n-input
          v-model:value="formModel.infoContactUrl"
          type="text"
          :placeholder="$t('models.platformSettings.infoContactUrl')"
          :disabled="loading"
          @keydown.enter.prevent
        />
      </n-form-item>
      <div style="display: flex; gap: var(--layout-gap); justify-content: end">
        <n-button secondary :disabled="!changed" @click="resetForm">{{
          $t('general.resetAction')
        }}</n-button>
        <n-button type="primary" :disabled="!changed" @click="handleSaveClick">{{
          $t('general.saveAction')
        }}</n-button>
      </div>
    </div>
    <div class="content-block">
      <h3>{{ $t('admin.system.platformSettings.headingOptions') }}</h3>

      <!-- DEFAULT TEXT -->
      <n-form-item :label="$t('models.platformSettings.defaultText')">
        <n-select
          v-model:value="formModel.defaultTextId"
          :options="defaultTextOptions"
          :clearable="true"
          :placeholder="$t('admin.system.platformSettings.defaultTextPlaceholder')"
          :consistent-menu-width="false"
          style="min-width: 200px"
          @keydown.enter.prevent
        />
      </n-form-item>
      <n-form-item :label="$t('admin.system.platformSettings.formLabelDisplay')">
        <div style="display: flex; flex-direction: column; gap: 4px">
          <!-- SHOW DESCIPTION IN HEADER? -->
          <n-checkbox
            v-model:checked="formModel.showHeaderInfo"
            :round="false"
            :disabled="loading"
            @keydown.enter.prevent
          >
            {{ $t('models.platformSettings.showHeaderInfo') }}
          </n-checkbox>
          <!-- SHOW TITLE AND DESCIPTION IN FOOTER? -->
          <n-checkbox
            v-model:checked="formModel.showFooterInfo"
            :round="false"
            :disabled="loading"
            @keydown.enter.prevent
          >
            {{ $t('models.platformSettings.showFooterInfo') }}
          </n-checkbox>
        </div>
      </n-form-item>
      <div style="display: flex; gap: var(--layout-gap); justify-content: end">
        <n-button secondary :disabled="!changed" @click="resetForm">{{
          $t('general.resetAction')
        }}</n-button>
        <n-button type="primary" :disabled="!changed" @click="handleSaveClick">{{
          $t('general.saveAction')
        }}</n-button>
      </div>
    </div>
  </n-form>
</template>
