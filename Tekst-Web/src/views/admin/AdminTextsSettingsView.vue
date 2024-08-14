<script setup lang="ts">
import { textFormRules } from '@/forms/formRules';
import { useMessages } from '@/composables/messages';
import { useStateStore } from '@/stores';
import {
  NSelect,
  NFlex,
  NButton,
  NForm,
  NFormItem,
  NInput,
  NDynamicInput,
  NColorPicker,
  type FormInst,
  useDialog,
} from 'naive-ui';
import { computed, ref, watch } from 'vue';
import { DELETE, PATCH } from '@/api';
import { $t } from '@/i18n';
import type { TextCreate } from '@/api';
import { useModelChanges } from '@/composables/modelChanges';
import { usePlatformData } from '@/composables/platformData';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import { dialogProps } from '@/common';
import _cloneDeep from 'lodash.clonedeep';
import TranslationFormItem from '@/forms/TranslationFormItem.vue';
import router from '@/router';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import LabelledSwitch from '@/components/LabelledSwitch.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import { SettingsIcon } from '@/icons';
import DynamicInputControls from '@/forms/DynamicInputControls.vue';

const state = useStateStore();
const { pfData, loadPlatformData } = usePlatformData();
const { message } = useMessages();
const dialog = useDialog();
const loading = ref(false);

const initialModel = () => _cloneDeep(state.text);

const model = ref<TextCreate | undefined>(initialModel());

const {
  changed: modelChanged,
  reset: resetModelChanges,
  getChanges: getModelChanges,
} = useModelChanges(model);

const formRef = ref<FormInst | null>(null);

const defaultLevelOptions = computed(() =>
  state.textLevelLabels.map((lbl, i: number) => ({
    label: lbl,
    value: i,
  }))
);

const textCanBeDeleted = computed(() => {
  if (!pfData.value) return false;
  if (state.text?.isActive) {
    return pfData.value.texts.filter((t) => t.isActive).length > 1;
  } else {
    return pfData.value.texts.length > 1;
  }
});

watch(
  () => state.text,
  () => {
    resetForm();
  }
);

function resetForm() {
  model.value = initialModel();
  resetModelChanges();
  formRef.value?.restoreValidation();
}

function handleSave() {
  loading.value = true;
  formRef.value
    ?.validate(async (validationError) => {
      if (validationError) return;
      const { data: updatedText, error } = await PATCH('/texts/{id}', {
        params: { path: { id: state.text?.id || '' } },
        body: getModelChanges(),
      });
      if (!error) {
        await loadPlatformData();
        state.text = updatedText;
        resetModelChanges();
        message.success($t('admin.text.settings.msgSaved'));
      }
      loading.value = false;
    })
    .catch(() => {
      message.error($t('errors.followFormRules'));
      loading.value = false;
    });
}

async function handleDelete() {
  dialog.warning({
    title: $t('general.warning'),
    content: $t('admin.text.settings.warnDeleteText', { title: state.text?.title || '?' }),
    positiveText: $t('general.yesAction'),
    negativeText: $t('general.noAction'),
    autoFocus: false,
    closable: false,
    ...dialogProps,
    onPositiveClick: async () => {
      loading.value = true;
      const { error } = await DELETE('/texts/{id}', {
        params: { path: { id: state.text?.id || '' } },
      });
      if (!error) {
        message.success($t('admin.text.settings.msgDeleted', { title: state.text?.title || '?' }));
        await loadPlatformData();
        state.text =
          pfData.value?.texts.find((t) => t.id == pfData.value?.state.defaultTextId) ||
          pfData.value?.texts[0];
        router.push({ name: 'home' });
      }
      loading.value = false;
    },
  });
}
</script>

<template>
  <icon-heading level="2" :icon="SettingsIcon">
    {{ $t('admin.text.settings.heading') }}
    <help-button-widget help-key="adminTextsSettingsView" />
  </icon-heading>

  <div v-if="model" class="content-block">
    <n-form
      ref="formRef"
      :model="model"
      :rules="textFormRules"
      :disabled="loading"
      label-placement="top"
      label-width="auto"
      require-mark-placement="right-hanging"
    >
      <!-- TITLE -->
      <n-form-item path="title" :label="$t('models.text.title')">
        <n-input
          v-model:value="model.title"
          type="text"
          :placeholder="$t('models.text.title')"
          @keydown.enter.prevent
        />
      </n-form-item>

      <!-- SUBTITLE -->
      <translation-form-item
        v-model="model.subtitle"
        parent-form-path-prefix="subtitle"
        :main-form-label="$t('models.text.subtitle')"
        :translation-form-label="$t('models.text.subtitle')"
        :translation-form-rule="textFormRules.subtitleTranslation"
      />

      <!-- SLUG -->
      <n-form-item path="slug" :label="$t('models.text.slug')">
        <n-input
          v-model:value="model.slug"
          type="text"
          :placeholder="$t('models.text.slug')"
          @keydown.enter.prevent
        />
      </n-form-item>

      <!-- DEFAULT STRUCTURE LEVEL-->
      <n-form-item path="defaultLevel" :label="$t('models.text.defaultLevel')">
        <n-select
          v-model:value="model.defaultLevel"
          :options="defaultLevelOptions"
          :disabled="loading || !defaultLevelOptions.length"
        />
      </n-form-item>

      <!-- LOCATION DELIMITER -->
      <n-form-item path="locDelim" :label="$t('models.text.locDelim')">
        <n-input
          v-model:value="model.locDelim"
          type="text"
          :placeholder="$t('models.text.locDelim')"
          @keydown.enter.prevent
        />
      </n-form-item>

      <n-form-item :show-label="false">
        <n-flex vertical>
          <!-- LABELLED LOCATION -->
          <labelled-switch
            v-model="model.labeledLocation"
            :label="$t('models.text.labeledLocation')"
          />
          <!-- ACTIVE -->
          <labelled-switch v-model="model.isActive" :label="$t('models.text.isActive')" />
        </n-flex>
      </n-form-item>

      <!-- ACCENT COLOR -->
      <n-form-item path="accentColor" :label="$t('models.text.accentColor')">
        <n-color-picker
          v-model:value="model.accentColor"
          :modes="['hex']"
          :show-alpha="false"
          :swatches="[
            '#305D97',
            '#3C8589',
            '#43895F',
            '#CC9618',
            '#BA5614',
            '#C62B26',
            '#B52651',
            '#88447F',
          ]"
        />
      </n-form-item>

      <!-- RESOURCE CATEGORIES-->
      <n-form-item v-if="model.resourceCategories" :label="$t('models.text.resourceCategories')">
        <n-dynamic-input
          v-model:value="model.resourceCategories"
          show-sort-button
          :min="0"
          :max="32"
          @create="() => ({ key: '', translations: [{ locale: '*', translation: '' }] })"
        >
          <template #default="{ index }">
            <div style="display: flex; align-items: flex-start; gap: 12px; width: 100%">
              <n-form-item
                ignore-path-change
                :label="$t('models.text.resourceCategoryKey')"
                :path="`resourceCategories[${index}].key`"
                :rule="textFormRules.resourceCategoryKey"
              >
                <n-input
                  v-model:value="model.resourceCategories[index].key"
                  :placeholder="$t('models.text.resourceCategoryKey')"
                  @keydown.enter.prevent
                />
              </n-form-item>
              <translation-form-item
                v-model="model.resourceCategories[index].translations"
                ignore-path-change
                secondary
                required
                :parent-form-path-prefix="`resourceCategories[${index}].translations`"
                style="flex-grow: 2"
                :main-form-label="$t('models.text.resourceCategoryTranslation')"
                :translation-form-label="$t('models.text.resourceCategoryTranslation')"
                :translation-form-rule="textFormRules.resourceCategoryTranslation"
              />
            </div>
          </template>
          <template #action="{ index: indexAction, create, remove, move }">
            <dynamic-input-controls
              top-offset
              :move-up-disabled="indexAction === 0"
              :move-down-disabled="indexAction === model.resourceCategories?.length - 1"
              :insert-disabled="(model.resourceCategories?.length || 0) >= 32"
              @move-up="() => move('up', indexAction)"
              @move-down="() => move('down', indexAction)"
              @remove="() => remove(indexAction)"
              @insert="() => create(indexAction)"
            />
          </template>
        </n-dynamic-input>
      </n-form-item>
    </n-form>

    <button-shelf top-gap>
      <template #start>
        <n-button secondary type="error" :disabled="!textCanBeDeleted" @click="handleDelete">
          {{ $t('general.deleteAction') }}
        </n-button>
      </template>
      <n-button secondary :disabled="loading || !modelChanged" @click="resetForm">
        {{ $t('general.resetAction') }}
      </n-button>
      <n-button
        type="primary"
        :loading="loading"
        :disabled="loading || !modelChanged"
        @click="handleSave"
      >
        {{ $t('general.saveAction') }}
      </n-button>
    </button-shelf>
  </div>
</template>
