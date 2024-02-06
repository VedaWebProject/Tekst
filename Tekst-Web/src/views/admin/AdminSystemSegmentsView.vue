<script setup lang="ts">
import { $t, getLocaleProfile, renderLanguageOptionLabel } from '@/i18n';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import HtmlEditor from '@/components/editors/HtmlEditor.vue';
import { computed, nextTick, ref } from 'vue';
import {
  NIcon,
  NButton,
  NSelect,
  NForm,
  NFormItem,
  NInput,
  type FormInst,
  useDialog,
  type InputInst,
} from 'naive-ui';
import { usePlatformData } from '@/composables/platformData';
import { PATCH, type ClientSegmentUpdate, POST, type ClientSegmentCreate, DELETE } from '@/api';
import HugeLabelledIcon from '@/components/generic/HugeLabelledIcon.vue';

import { useI18n } from 'vue-i18n';
import { useModelChanges } from '@/composables/modelChanges';
import { useMessages } from '@/composables/messages';
import { systemSegmentFormRules } from '@/forms/formRules';
import { dialogProps } from '@/common';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import { useStateStore } from '@/stores';

import { AddIcon, FileOpenIcon } from '@/icons';

const state = useStateStore();
const { pfData, loadPlatformData } = usePlatformData();
const { locale } = useI18n();
const { message } = useMessages();
const dialog = useDialog();

const loading = ref(false);
const formRef = ref<FormInst | null>(null);
const selectedSegmentId = ref<string | null>(null);
const segmentModel = ref<ClientSegmentUpdate>();
const firstInputRef = ref<InputInst>();

const {
  changed: modelChanged,
  reset: resetModelChanges,
  getChanges: getModelChanges,
} = useModelChanges(segmentModel);

const segmentOptions = computed(() =>
  [...new Set(pfData.value?.systemSegments.map((s) => s.key))].map((key) => {
    const groupSegments = pfData.value?.systemSegments.filter((s) => s.key === key) || [];
    const currLocaleSegment =
      groupSegments.find((s) => s.locale === locale.value) ||
      groupSegments.find((s) => s.locale === '*') ||
      groupSegments.find((s) => s.locale === 'enUS') ||
      groupSegments[0];
    return {
      type: 'group',
      label: currLocaleSegment.title || currLocaleSegment.key,
      key,
      children: groupSegments.map((s) => ({
        label: (getLocaleProfile(s.locale)?.icon || '🌐') + ' ' + (s.title || s.key),
        value: s.id,
      })),
    };
  })
);

const localeOptions = computed(() =>
  state.translationLocaleOptions.map((tlo) => ({
    ...tlo,
    disabled: !!pfData.value?.systemSegments.find(
      (p) =>
        p.locale === tlo.value &&
        p.key === segmentModel.value?.key &&
        p.id !== selectedSegmentId.value
    ),
  }))
);

const systemSegmentKeys = [
  'systemHome',
  'systemHeadEnd',
  'systemBodyEnd',
  'systemFooter',
  'systemSiteNotice',
  'systemPrivacyPolicy',
];

const systemSegmentKeyOptions = systemSegmentKeys.map((key) => ({
  label: () => $t(`admin.system.segments.systemKeys.${key}`),
  value: key,
}));

function getSegmentModel(segmentId?: string): ClientSegmentUpdate {
  if (!segmentId) {
    return {
      key: '',
      title: null,
      locale: null,
      editorMode: 'wysiwyg',
      html: '',
    };
  } else {
    const selectedSegment = pfData.value?.systemSegments.find((s) => s.id === segmentId);
    if (!selectedSegment) {
      return getSegmentModel();
    } else {
      return Object.assign({}, selectedSegment);
    }
  }
}

function handleAddSegmentClick() {
  selectedSegmentId.value = null;
  segmentModel.value = getSegmentModel();
  resetModelChanges();
  formRef.value?.restoreValidation();
  nextTick(() => firstInputRef.value?.focus());
}

function handleSelectSegment(id: string) {
  segmentModel.value = getSegmentModel(id);
  resetModelChanges();
  formRef.value?.restoreValidation();
}

async function handleSaveClick() {
  loading.value = true;
  formRef.value
    ?.validate(async (validationError) => {
      if (validationError) return;
      if (selectedSegmentId.value) {
        await updateSegment();
      } else {
        await createSegment();
      }
    })
    .catch(() => {
      message.error($t('errors.followFormRules'));
      loading.value = false;
    });
  loading.value = false;
}

async function updateSegment() {
  const { data, error } = await PATCH('/platform/segments/{id}', {
    params: { path: { id: selectedSegmentId.value || '' } },
    body: getModelChanges(),
  });
  if (!error) {
    message.success(
      $t('admin.system.segments.msgUpdated', {
        title: segmentModel.value?.title || segmentModel.value?.key || '',
      })
    );
    selectedSegmentId.value = data.id;
    segmentModel.value = data;
    resetModelChanges();
    loadPlatformData();
  }
}

async function createSegment() {
  const { data, error } = await POST('/platform/segments', {
    body: segmentModel.value as ClientSegmentCreate,
  });
  if (!error) {
    message.success(
      $t('admin.system.segments.msgCreated', {
        title: segmentModel.value?.title || segmentModel.value?.key || '',
      })
    );
    selectedSegmentId.value = data.id;
    segmentModel.value = data;
    resetModelChanges();
    loadPlatformData();
  }
}

function handleCancelClick() {
  if (!modelChanged.value) {
    resetForm();
    return;
  }
  dialog.warning({
    title: $t('general.warning'),
    content: $t('admin.system.segments.warnCancel'),
    positiveText: $t('general.yesAction'),
    negativeText: $t('general.noAction'),
    autoFocus: false,
    closable: false,
    ...dialogProps,
    onPositiveClick: resetForm,
  });
}

function resetForm() {
  selectedSegmentId.value = null;
  segmentModel.value = undefined;
  resetModelChanges();
  formRef.value?.restoreValidation();
}

async function handleDeleteClick() {
  if (!selectedSegmentId.value) return;

  dialog.warning({
    title: $t('general.warning'),
    content: $t('admin.system.segments.warnDelete', {
      title: segmentModel.value?.title || segmentModel.value?.key || '',
    }),
    positiveText: $t('general.yesAction'),
    negativeText: $t('general.noAction'),
    autoFocus: false,
    closable: false,
    ...dialogProps,
    onPositiveClick: async () => {
      const { error } = await DELETE('/platform/segments/{id}', {
        params: { path: { id: selectedSegmentId.value || '' } },
      });
      if (!error) {
        message.success(
          $t('admin.system.segments.msgDeleted', {
            title: segmentModel.value?.title || segmentModel.value?.key || '',
          })
        );
      }
      resetForm();
      loadPlatformData();
    },
  });
}
</script>

<template>
  <h2>
    {{ $t('admin.system.segments.heading') }}
    <help-button-widget help-key="adminSystemSegmentsView" />
  </h2>

  <div style="display: flex; gap: var(--layout-gap)">
    <n-select
      v-model:value="selectedSegmentId"
      filterable
      size="large"
      :disabled="modelChanged"
      :options="segmentOptions"
      :placeholder="
        modelChanged
          ? $t('admin.system.segments.newSegment')
          : $t('admin.system.segments.phSelectSegment')
      "
      style="flex-grow: 2"
      @update:value="handleSelectSegment"
    />
    <n-button type="primary" :disabled="modelChanged" size="large" @click="handleAddSegmentClick">
      <template #icon>
        <n-icon :component="AddIcon" />
      </template>
    </n-button>
  </div>

  <template v-if="segmentModel">
    <div class="content-block">
      <n-form
        ref="formRef"
        :model="segmentModel"
        :rules="systemSegmentFormRules"
        :disabled="loading"
        label-placement="top"
        label-width="auto"
        require-mark-placement="right-hanging"
      >
        <!-- TITLE -->
        <n-form-item path="title" :label="$t('models.segment.title')">
          <n-input
            ref="firstInputRef"
            v-model:value="segmentModel.title"
            type="text"
            :placeholder="$t('models.segment.title')"
            @keydown.enter.prevent
          />
        </n-form-item>
        <!-- KEY -->
        <n-form-item path="key" :label="$t('models.segment.key')">
          <n-select
            v-model:value="segmentModel.key"
            :options="systemSegmentKeyOptions"
            :placeholder="$t('models.segment.key')"
            :consistent-menu-width="false"
            style="min-width: 200px"
            @keydown.enter.prevent
          />
        </n-form-item>
        <!-- LOCALE -->
        <n-form-item path="locale" :label="$t('models.segment.locale')">
          <n-select
            v-model:value="segmentModel.locale"
            :options="localeOptions"
            :placeholder="$t('general.language')"
            :consistent-menu-width="false"
            :render-label="(o) => renderLanguageOptionLabel(localeOptions, o)"
            style="min-width: 200px"
            @keydown.enter.prevent
          />
        </n-form-item>
        <!-- HTML -->
        <n-form-item path="html" :label="$t('models.segment.html')">
          <html-editor
            v-model:value="segmentModel.html"
            v-model:editor-mode="segmentModel.editorMode"
            :max-chars="1048576"
            toolbar-size="medium"
          />
        </n-form-item>
      </n-form>

      <button-shelf top-gap>
        <template #start>
          <n-button v-if="selectedSegmentId" secondary type="error" @click="handleDeleteClick">
            {{ $t('general.deleteAction') }}
          </n-button>
        </template>
        <n-button secondary @click="handleCancelClick">{{ $t('general.cancelAction') }}</n-button>
        <n-button
          type="primary"
          :loading="loading"
          :disabled="!modelChanged"
          @click="handleSaveClick"
          >{{ $t('general.saveAction') }}</n-button
        >
      </button-shelf>
    </div>
  </template>

  <huge-labelled-icon
    v-else
    :message="$t('admin.system.segments.noSegment')"
    :icon="FileOpenIcon"
  />
</template>
