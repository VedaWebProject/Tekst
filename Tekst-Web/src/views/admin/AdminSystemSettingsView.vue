<script setup lang="ts">
import { $t } from '@/i18n';
import HelpButtonWidget from '@/components/widgets/HelpButtonWidget.vue';
import { ref } from 'vue';
import {
  NIcon,
  NDynamicInput,
  NCheckbox,
  NButton,
  NButtonGroup,
  NSelect,
  NForm,
  NFormItem,
  NInput,
  type FormInst,
} from 'naive-ui';
import { usePlatformData } from '@/platformData';
import { PATCH, type PlatformSettingsUpdate } from '@/api';
import { useModelChanges } from '@/modelChanges';
import { useMessages } from '@/messages';
import { platformSettingsFormRules } from '@/forms/formRules';
import TranslationFormItem from '@/forms/TranslationFormItem.vue';

import AddOutlined from '@vicons/material/AddOutlined';
import MinusRound from '@vicons/material/MinusRound';
import ArrowUpwardOutlined from '@vicons/material/ArrowUpwardOutlined';
import ArrowDownwardOutlined from '@vicons/material/ArrowDownwardOutlined';
import ButtonFooter from '@/components/ButtonFooter.vue';

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
    :disabled="loading"
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
          @keydown.enter.prevent
        />
      </n-form-item>
      <!-- PLATFORM DESCRIPTION -->
      <TranslationFormItem
        v-model:value="formModel.infoSubtitle"
        parent-form-path-prefix="infoSubtitle"
        :loading="loading"
        :main-form-label="$t('models.platformSettings.infoSubtitle')"
        :translation-form-label="$t('models.platformSettings.infoSubtitle')"
        :translation-form-rule="platformSettingsFormRules.infoSubtitleTranslation"
      />
      <!-- TERMS URL -->
      <n-form-item path="infoTerms" :label="$t('models.platformSettings.infoTerms')">
        <n-input
          v-model:value="formModel.infoTerms"
          type="text"
          :placeholder="$t('models.platformSettings.infoTerms')"
          @keydown.enter.prevent
        />
      </n-form-item>
      <!-- CONTACT NAME -->
      <n-form-item path="infoContactName" :label="$t('models.platformSettings.infoContactName')">
        <n-input
          v-model:value="formModel.infoContactName"
          type="text"
          :placeholder="$t('models.platformSettings.infoContactName')"
          @keydown.enter.prevent
        />
      </n-form-item>
      <!-- CONTACT EMAIL -->
      <n-form-item path="infoContactEmail" :label="$t('models.platformSettings.infoContactEmail')">
        <n-input
          v-model:value="formModel.infoContactEmail"
          type="text"
          :placeholder="$t('models.platformSettings.infoContactEmail')"
          @keydown.enter.prevent
        />
      </n-form-item>
      <!-- CONTACT URL -->
      <n-form-item path="infoContactUrl" :label="$t('models.platformSettings.infoContactUrl')">
        <n-input
          v-model:value="formModel.infoContactUrl"
          type="text"
          :placeholder="$t('models.platformSettings.infoContactUrl')"
          @keydown.enter.prevent
        />
      </n-form-item>
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

      <!-- TRANSLATE MAIN NAV INFO ENTRY -->
      <TranslationFormItem
        v-model:value="formModel.navInfoEntry"
        parent-form-path-prefix="navInfoEntry"
        :loading="loading"
        :main-form-label="$t('models.platformSettings.navInfoEntry')"
        :translation-form-label="$t('models.platformSettings.navInfoEntry')"
        :translation-form-rule="platformSettingsFormRules.navInfoEntryTranslation"
      />

      <!-- DISPLAY OPTIONS -->
      <n-form-item :label="$t('admin.system.platformSettings.formLabelDisplay')">
        <div style="display: flex; flex-direction: column; gap: 4px">
          <!-- ALWAY SHOW TEXT INFO, ALSO ON NON-TEXT-SPECIFIC PAGES? -->
          <n-checkbox
            v-model:checked="formModel.alwaysShowTextInfo"
            :round="false"
            @keydown.enter.prevent
          >
            {{ $t('models.platformSettings.alwaysShowTextInfo') }}
          </n-checkbox>
          <!-- SHOW DESCIPTION IN HEADER? -->
          <n-checkbox
            v-model:checked="formModel.showHeaderInfo"
            :round="false"
            @keydown.enter.prevent
          >
            {{ $t('models.platformSettings.showHeaderInfo') }}
          </n-checkbox>
          <!-- SHOW TITLE AND DESCIPTION IN FOOTER? -->
          <n-checkbox
            v-model:checked="formModel.showFooterInfo"
            :round="false"
            @keydown.enter.prevent
          >
            {{ $t('models.platformSettings.showFooterInfo') }}
          </n-checkbox>
        </div>
      </n-form-item>
    </div>

    <div class="content-block">
      <h3>{{ $t('models.platformSettings.layerCategories') }}</h3>
      <!-- LAYER CATEGORIES-->
      <n-form-item v-if="formModel.layerCategories" :show-label="false">
        <n-dynamic-input
          v-model:value="formModel.layerCategories"
          item-style="margin-bottom: 0;"
          show-sort-button
          :min="0"
          :max="64"
          @create="() => ({ key: '', translations: [{ locale: '*', translation: '' }] })"
        >
          <template #default="{ index }">
            <div style="display: flex; align-items: flex-start; gap: 12px; width: 100%">
              <n-form-item
                ignore-path-change
                :label="$t('models.platformSettings.layerCategoryKey')"
                :path="`layerCategories[${index}].key`"
                :rule="platformSettingsFormRules.layerCategoryKey"
                required
              >
                <n-input
                  v-model:value="formModel.layerCategories[index].key"
                  :placeholder="$t('models.platformSettings.layerCategoryKey')"
                  @keydown.enter.prevent
                />
              </n-form-item>
              <TranslationFormItem
                v-model:value="formModel.layerCategories[index].translations"
                :parent-form-path-prefix="`layerCategories[${index}].translations`"
                required
                style="flex-grow: 2; padding: 0 var(--layout-gap)"
                :main-form-label="$t('models.platformSettings.layerCategoryTranslation')"
                :translation-form-label="$t('models.platformSettings.layerCategoryTranslation')"
                :translation-form-rule="platformSettingsFormRules.layerCategoryTranslation"
              />
            </div>
          </template>
          <template #action="{ index: indexAction, create, remove, move }">
            <n-button-group style="margin-left: var(--layout-gap); padding-top: 26px">
              <n-button
                type="primary"
                secondary
                :title="$t('general.removeAction')"
                :focusable="false"
                @click="() => remove(indexAction)"
              >
                <template #icon>
                  <n-icon :component="MinusRound" />
                </template>
              </n-button>
              <n-button
                type="primary"
                secondary
                :title="$t('general.insertAction')"
                :disabled="(formModel.layerCategories?.length || 0) >= 64"
                :focusable="false"
                @click="() => create(indexAction)"
              >
                <template #icon>
                  <n-icon :component="AddOutlined" />
                </template>
              </n-button>
              <n-button
                type="primary"
                secondary
                :title="$t('general.moveUpAction')"
                :disabled="indexAction === 0"
                :focusable="false"
                @click="() => move('up', indexAction)"
              >
                <template #icon>
                  <n-icon :component="ArrowUpwardOutlined" />
                </template>
              </n-button>
              <n-button
                type="primary"
                secondary
                :title="$t('general.moveDownAction')"
                :disabled="indexAction === formModel.layerCategories?.length - 1"
                :focusable="false"
                @click="() => move('down', indexAction)"
              >
                <template #icon>
                  <n-icon :component="ArrowDownwardOutlined" />
                </template>
              </n-button>
            </n-button-group>
          </template>
        </n-dynamic-input>
      </n-form-item>
      <!-- SHOW LAYER CATEGORY HEADINGS -->
      <n-form-item :show-label="false">
        <n-checkbox
          v-model:checked="formModel.showLayerCategoryHeadings"
          :round="false"
          @keydown.enter.prevent
        >
          {{ $t('models.platformSettings.showLayerCategoryHeadings') }}
        </n-checkbox>
      </n-form-item>
    </div>
  </n-form>
  <ButtonFooter style="margin-bottom: var(--layout-gap)">
    <n-button secondary :disabled="!changed" @click="resetForm">{{
      $t('general.resetAction')
    }}</n-button>
    <n-button type="primary" :disabled="!changed" @click="handleSaveClick">{{
      $t('general.saveAction')
    }}</n-button>
  </ButtonFooter>
</template>
