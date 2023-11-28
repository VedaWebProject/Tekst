<script setup lang="ts">
import { textFormRules } from '@/formRules';
import { useMessages } from '@/messages';
import { useStateStore } from '@/stores';
import {
  NCheckbox,
  NSelect,
  NSpace,
  NButton,
  NForm,
  NFormItem,
  NInput,
  NIcon,
  NColorPicker,
  NDynamicInput,
  type FormInst,
  useDialog,
} from 'naive-ui';
import { computed, ref, watch } from 'vue';
import { DELETE, PATCH } from '@/api';
import { $t } from '@/i18n';
import { localeProfiles } from '@/i18n';
import type { SubtitleTranslation, TextCreate } from '@/api';
import { useModelChanges } from '@/modelChanges';
import { usePlatformData } from '@/platformData';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import { negativeButtonProps, positiveButtonProps } from '@/components/dialogButtonProps';
import _cloneDeep from 'lodash.clonedeep';

import AddRound from '@vicons/material/AddRound';
import MinusRound from '@vicons/material/MinusRound';
import router from '@/router';

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

const subtitleLocaleOptions = computed(() =>
  Object.keys(localeProfiles).map((l) => ({
    label: `${localeProfiles[l].icon} ${localeProfiles[l].displayFull}`,
    value: l,
    disabled: !!model.value?.subtitle?.find((s: SubtitleTranslation) => s && s.locale == l),
  }))
);

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
    model.value = initialModel();
    resetModelChanges();
  }
);

function handleReset() {
  model.value = initialModel();
  resetModelChanges();
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
        message.success($t('admin.text.general.msgSaved'));
      } else {
        /**
         * This will be either an app-level error (e.g. buggy validation, server down, 401)
         * or the provided email already exists, which we don't want to actively disclose.
         */
        message.error($t('errors.unexpected'));
      }
      loading.value = false;
    })
    .catch(() => {
      message.error($t('errors.followFormRules'));
      loading.value = false;
    });
}

async function handleDelete() {
  loading.value = true;
  dialog.warning({
    title: $t('general.warning'),
    content: $t('admin.text.general.warnDeleteText', { title: state.text?.title || '?' }),
    positiveText: $t('general.yesAction'),
    negativeText: $t('general.noAction'),
    positiveButtonProps,
    negativeButtonProps,
    autoFocus: false,
    closable: false,
    onPositiveClick: async () => {
      const { error } = await DELETE('/texts/{id}', {
        params: { path: { id: state.text?.id || '' } },
      });
      if (!error) {
        message.success($t('admin.text.general.msgDeleted', { title: state.text?.title || '?' }));
        await loadPlatformData();
        state.text =
          pfData.value?.texts.find((t) => t.id == pfData.value?.settings.defaultTextId) ||
          pfData.value?.texts[0];
        router.push({ name: 'home' });
      } else {
        message.error($t('errors.unexpected'), error);
      }
    },
  });
}
</script>

<template>
  <h2>
    {{ $t('admin.text.general.heading') }}
    <HelpButtonWidget help-key="adminTextsGeneralView" />
  </h2>

  <div v-if="model" class="content-block">
    <n-form
      ref="formRef"
      :model="model"
      :rules="textFormRules"
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
          :disabled="loading"
          @keydown.enter.prevent
        />
      </n-form-item>

      <!-- SUBTITLE -->
      <n-form-item v-if="model.subtitle" :label="$t('models.text.subtitle')">
        <n-dynamic-input
          v-model:value="model.subtitle"
          item-style="margin-bottom: 0;"
          :min="0"
          :max="Object.keys(localeProfiles).length"
          @create="() => ({ locale: null, subtitle: '' })"
        >
          <template #default="{ index: subtitleIndex }">
            <div style="display: flex; align-items: flex-start; gap: 12px; width: 100%">
              <n-form-item
                ignore-path-change
                :show-label="false"
                :path="`subtitle[${subtitleIndex}].locale`"
                :rule="textFormRules.subtitleLocale"
                required
              >
                <n-select
                  v-model:value="model.subtitle[subtitleIndex].locale"
                  :options="subtitleLocaleOptions"
                  :placeholder="$t('general.language')"
                  :consistent-menu-width="false"
                  style="min-width: 200px"
                  @keydown.enter.prevent
                />
              </n-form-item>
              <n-form-item
                ignore-path-change
                :show-label="false"
                :path="`subtitle[${subtitleIndex}].subtitle`"
                :rule="textFormRules.subtitle"
                style="flex-grow: 2"
              >
                <n-input
                  v-model:value="model.subtitle[subtitleIndex].subtitle"
                  :placeholder="$t('models.text.subtitle')"
                  @keydown.enter.prevent
                />
              </n-form-item>
            </div>
          </template>
          <template #action="{ index: indexAction, create, remove }">
            <n-space style="margin-left: 20px; flex-wrap: nowrap">
              <n-button
                secondary
                circle
                :title="$t('general.removeAction')"
                @click="() => remove(indexAction)"
              >
                <template #icon>
                  <n-icon :component="MinusRound" />
                </template>
              </n-button>
              <n-button
                secondary
                circle
                :title="$t('general.insertAction')"
                :disabled="model.subtitle.length >= Object.keys(localeProfiles).length"
                @click="() => create(indexAction)"
              >
                <template #icon>
                  <n-icon :component="AddRound" />
                </template>
              </n-button>
            </n-space>
          </template>
        </n-dynamic-input>
      </n-form-item>

      <!-- SLUG -->
      <n-form-item path="slug" :label="$t('models.text.slug')">
        <n-input
          v-model:value="model.slug"
          type="text"
          :placeholder="$t('models.text.slug')"
          :disabled="loading"
          @keydown.enter.prevent
        />
      </n-form-item>

      <!-- DEFAULT STRUCTURE LEVEL-->
      <n-form-item path="defaultLevel" :label="$t('models.text.defaultLevel')">
        <n-select
          v-model:value="model.defaultLevel"
          :options="defaultLevelOptions"
          :disabled="loading || !defaultLevelOptions.length"
          style="font-weight: var(--app-ui-font-weight-normal)"
        />
      </n-form-item>

      <!-- LOCATION DELIMITER -->
      <n-form-item path="locDelim" :label="$t('models.text.locDelim')">
        <n-input
          v-model:value="model.locDelim"
          type="text"
          :placeholder="$t('models.text.locDelim')"
          :disabled="loading"
          @keydown.enter.prevent
        />
      </n-form-item>

      <!-- ACCENT COLOR -->
      <n-form-item path="accentColor" :label="$t('models.text.accentColor')">
        <n-color-picker
          v-model:value="model.accentColor"
          :modes="['hex']"
          :show-alpha="false"
          :disabled="loading"
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

      <n-form-item :label="$t('general.flags')">
        <n-space vertical>
          <!-- LABELED LOCATION -->
          <n-checkbox v-model:checked="model.labeledLocation" :disabled="loading">
            {{ $t('models.text.labeledLocation') }}
          </n-checkbox>
          <!-- ACTIVE -->
          <n-checkbox v-model:checked="model.isActive" :disabled="loading">
            {{ $t('models.text.isActive') }}
          </n-checkbox>
        </n-space>
      </n-form-item>
    </n-form>

    <div style="display: flex; gap: var(--layout-gap); margin-top: 0.5rem">
      <n-button secondary :disabled="!textCanBeDeleted" @click="handleDelete">
        {{ $t('general.deleteAction') }}
      </n-button>
      <div style="flex-grow: 2"></div>
      <n-button
        secondary
        :loading="loading"
        :disabled="loading || !modelChanged"
        @click="() => handleReset"
      >
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
    </div>
  </div>
</template>
