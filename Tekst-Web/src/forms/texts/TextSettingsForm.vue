<script setup lang="ts">
import type { TextCreate } from '@/api';
import { PATCH, colorPresets } from '@/api';
import { dynInputCreateBtnProps } from '@/common';
import FormSection from '@/components/FormSection.vue';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import LabeledSwitch from '@/components/LabeledSwitch.vue';
import { useMessages } from '@/composables/messages';
import { useModelChanges } from '@/composables/modelChanges';
import { usePlatformData } from '@/composables/platformData';
import DynamicInputControls from '@/forms/DynamicInputControls.vue';
import { textFormRules } from '@/forms/formRules';
import TranslationFormItem from '@/forms/TranslationFormItem.vue';
import { $t } from '@/i18n';
import { useStateStore } from '@/stores';
import { pickTranslation } from '@/utils';
import { cloneDeep } from 'lodash-es';
import {
  NAlert,
  NButton,
  NColorPicker,
  NDynamicInput,
  NFlex,
  NForm,
  NFormItem,
  NInput,
  NSelect,
  type FormInst,
} from 'naive-ui';
import { computed, ref, watch } from 'vue';
import { onBeforeRouteUpdate } from 'vue-router';

const state = useStateStore();
const { loadPlatformData } = usePlatformData();
const { message } = useMessages();
const loading = ref(false);

const initialModel = () => cloneDeep(state.text);

const model = ref<TextCreate | undefined>(initialModel());

const {
  changed: modelChanged,
  reset: resetModelChanges,
  getChanges: getModelChanges,
} = useModelChanges(model);

const formRef = ref<FormInst | null>(null);

const defaultLevelOptions = computed(
  () =>
    model.value?.levels.map((lvl, i: number) => ({
      label: pickTranslation(lvl, state.locale),
      value: i,
    })) || []
);

const slugChangeWarning = computed(() => {
  if (!model.value || !state.text) return undefined;
  if (model.value.slug !== state.text.slug) {
    return $t('models.text.slugChangeWarning');
  }
  return undefined;
});

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
        message.success($t('texts.settings.msgSaved'));
      }
      loading.value = false;
    })
    .catch(() => {
      message.error($t('errors.followFormRules'));
      loading.value = false;
    });
}

watch(
  () => state.text?.id,
  () => {
    resetForm();
  }
);

onBeforeRouteUpdate((to, from) => {
  if (to.params.textSlug !== from.params.textSlug) {
    resetForm();
  }
});
</script>

<template>
  <div v-if="model">
    <n-form
      ref="formRef"
      :model="model"
      :rules="textFormRules"
      :disabled="loading"
      label-placement="top"
      label-width="auto"
      require-mark-placement="right-hanging"
    >
      <form-section :title="$t('common.general')">
        <!-- TITLE -->
        <n-form-item path="title" :label="$t('common.title')">
          <n-input
            v-model:value="model.title"
            type="text"
            :placeholder="$t('common.title')"
            @keydown.enter.prevent
          />
        </n-form-item>

        <!-- SUBTITLE -->
        <translation-form-item
          v-model="model.subtitle"
          parent-form-path-prefix="subtitle"
          :main-form-label="$t('common.subtitle')"
          :translation-form-label="$t('common.subtitle')"
          :translation-form-rules="textFormRules.subtitleTranslation"
        />

        <!-- SLUG -->
        <n-alert
          v-if="slugChangeWarning"
          type="warning"
          :title="$t('models.text.slugChangeWarning')"
          class="mb-md"
        />
        <n-form-item path="slug" :label="$t('models.text.slug')">
          <n-input
            v-model:value="model.slug"
            type="text"
            :placeholder="$t('models.text.slug')"
            :style="{ backgroundColor: slugChangeWarning ? 'var(--warning-color)' : undefined }"
            :input-props="{ style: { color: slugChangeWarning ? 'var(--base-color)' : undefined } }"
            @keydown.enter.prevent
          />
        </n-form-item>

        <!-- DEFAULT STRUCTURE LEVEL -->
        <n-form-item path="defaultLevel" :label="$t('models.text.defaultLevel')">
          <n-select
            v-model:value="model.defaultLevel"
            :options="defaultLevelOptions"
            :disabled="!defaultLevelOptions.length"
          />
        </n-form-item>

        <!-- ACTIVE -->
        <n-form-item :show-label="false" :show-feedback="false">
          <labeled-switch v-model="model.isActive" :label="$t('models.text.isActive')" />
        </n-form-item>
      </form-section>

      <form-section :title="$t('common.presentation')">
        <!-- LOCATION DELIMITER -->
        <n-form-item path="locDelim" :label="$t('models.text.locDelim')">
          <n-input
            v-model:value="model.locDelim"
            type="text"
            :placeholder="$t('models.text.locDelim')"
            @keydown.enter.prevent
          />
        </n-form-item>

        <!-- LABELLED LOCATION -->
        <n-form-item :show-label="false" :show-feedback="false">
          <labeled-switch
            v-model="model.labeledLocation"
            :label="$t('models.text.labeledLocation')"
          />
        </n-form-item>

        <!-- USE FULL LOCATION LABEL AS SEARCH HIT HEADING -->
        <n-form-item :show-label="false">
          <labeled-switch
            v-model="model.fullLocLabelAsHitHeading"
            :label="$t('models.text.fullLocLabelAsHitHeading')"
          />
        </n-form-item>

        <!-- COLOR -->
        <n-form-item path="color" :label="$t('models.text.color')">
          <n-color-picker
            v-model:value="model.color"
            :modes="['hex']"
            :show-alpha="false"
            :swatches="colorPresets"
          />
        </n-form-item>
      </form-section>

      <!-- RESOURCE CATEGORIES -->
      <form-section :title="$t('models.text.resourceCategories')">
        <n-form-item v-if="model.resourceCategories" :show-label="false">
          <n-dynamic-input
            v-model:value="model.resourceCategories"
            show-sort-button
            :min="0"
            :max="32"
            :create-button-props="dynInputCreateBtnProps"
            item-class="divided"
            @create="() => ({ key: '', translations: [{ locale: '*', translation: '' }] })"
          >
            <template #default="{ index }">
              <n-flex align="flex-start" style="width: 100%">
                <n-form-item
                  ignore-path-change
                  :label="$t('common.key')"
                  :path="`resourceCategories[${index}].key`"
                  :rule="textFormRules.resourceCategoryKey"
                >
                  <n-input
                    v-model:value="model.resourceCategories[index].key"
                    :placeholder="$t('common.key')"
                    @keydown.enter.prevent
                  />
                </n-form-item>
                <translation-form-item
                  v-model="model.resourceCategories[index].translations"
                  ignore-path-change
                  secondary
                  :parent-form-path-prefix="`resourceCategories[${index}].translations`"
                  style="flex: 2"
                  :main-form-label="$t('common.label')"
                  :translation-form-label="$t('common.label')"
                  :translation-form-rules="textFormRules.resourceCategoryTranslation"
                />
              </n-flex>
            </template>
            <template #action="{ index, create, remove, move }">
              <dynamic-input-controls
                top-offset
                :move-up-disabled="index === 0"
                :move-down-disabled="index === model.resourceCategories?.length - 1"
                :insert-disabled="(model.resourceCategories?.length || 0) >= 32"
                @move-up="() => move('up', index)"
                @move-down="() => move('down', index)"
                @remove="() => remove(index)"
                @insert="() => create(index)"
              />
            </template>
            <template #create-button-default>
              {{ $t('common.add') }}
            </template>
          </n-dynamic-input>
        </n-form-item>
      </form-section>
    </n-form>

    <button-shelf top-gap>
      <n-button secondary :disabled="loading || !modelChanged" @click="resetForm">
        {{ $t('common.reset') }}
      </n-button>
      <n-button
        type="primary"
        :loading="loading"
        :disabled="loading || !modelChanged"
        @click="handleSave"
      >
        {{ $t('common.save') }}
      </n-button>
    </button-shelf>
  </div>
</template>
