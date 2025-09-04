<script setup lang="ts">
import { DELETE, PATCH, POST, type ClientSegmentCreate, type ClientSegmentUpdate } from '@/api';
import { dialogProps } from '@/common';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import HtmlEditor from '@/components/editors/HtmlEditor.vue';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import { useMessages } from '@/composables/messages';
import { useModelChanges } from '@/composables/modelChanges';
import { usePlatformData } from '@/composables/platformData';
import { systemSegmentFormRules } from '@/forms/formRules';
import { $t, getLocaleProfile, renderLanguageOptionLabel } from '@/i18n';
import { AddIcon, FileOpenIcon, SegmentsIcon } from '@/icons';
import { useStateStore } from '@/stores';
import {
  NButton,
  NEmpty,
  NFlex,
  NForm,
  NFormItem,
  NIcon,
  NInput,
  NSelect,
  useDialog,
  type FormInst,
  type InputInst,
} from 'naive-ui';
import { computed, nextTick, ref } from 'vue';

const state = useStateStore();
const { loadPlatformData } = usePlatformData();
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
  [...new Set(state.pf?.systemSegments.map((s) => s.key))].map((key) => {
    const groupSegments = state.pf?.systemSegments.filter((s) => s.key === key) || [];
    return {
      type: 'group',
      label: $t(`admin.segments.systemKeys.${key}`),
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
    disabled: !!state.pf?.systemSegments.find(
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
  'systemFooterUpper',
  'systemFooterLower',
  'systemSiteNotice',
  'systemPrivacyPolicy',
  'systemRegisterIntro',
];

const systemSegmentKeyOptions = systemSegmentKeys.map((key) => ({
  label: () => $t(`admin.segments.systemKeys.${key}`),
  value: key,
}));

function getSegmentModel(segmentId?: string): ClientSegmentUpdate {
  if (!segmentId) {
    return {
      key: '',
      title: undefined,
      locale: '*',
      editorMode: 'wysiwyg',
      html: '',
    };
  } else {
    const selectedSegment = state.pf?.systemSegments.find((s) => s.id === segmentId);
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
    body: getModelChanges() as ClientSegmentUpdate,
  });
  if (!error) {
    message.success(
      $t('admin.segments.msgUpdated', {
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
      $t('admin.segments.msgCreated', {
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
    title: $t('common.warning'),
    content: $t('admin.segments.warnCancel'),
    positiveText: $t('common.yes'),
    negativeText: $t('common.no'),
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
    title: $t('common.warning'),
    content: $t('admin.segments.warnDelete', {
      title: segmentModel.value?.title || segmentModel.value?.key || '',
    }),
    positiveText: $t('common.yes'),
    negativeText: $t('common.no'),
    closable: false,
    ...dialogProps,
    onPositiveClick: async () => {
      const { error } = await DELETE('/platform/segments/{id}', {
        params: { path: { id: selectedSegmentId.value || '' } },
      });
      if (!error) {
        message.success(
          $t('admin.segments.msgDeleted', {
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
  <icon-heading level="1" :icon="SegmentsIcon">
    {{ $t('admin.segments.heading') }}
    <help-button-widget help-key="adminSegmentsView" />
  </icon-heading>

  <n-flex :wrap="false">
    <n-select
      v-model:value="selectedSegmentId"
      filterable
      size="large"
      :disabled="modelChanged"
      :options="segmentOptions"
      :placeholder="
        modelChanged ? $t('admin.segments.newSegment') : $t('admin.segments.phSelectSegment')
      "
      style="flex: 2"
      @update:value="handleSelectSegment"
    />
    <n-button type="primary" :disabled="modelChanged" size="large" @click="handleAddSegmentClick">
      <template #icon>
        <n-icon :component="AddIcon" />
      </template>
    </n-button>
  </n-flex>

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
        <n-form-item path="title" :label="$t('common.title')">
          <n-input
            ref="firstInputRef"
            v-model:value="segmentModel.title"
            type="text"
            :placeholder="$t('common.title')"
            @keydown.enter.prevent
          />
        </n-form-item>
        <!-- KEY -->
        <n-form-item path="key" :label="$t('common.type')">
          <n-select
            v-model:value="segmentModel.key"
            :options="systemSegmentKeyOptions"
            :consistent-menu-width="false"
            style="min-width: 200px"
            @keydown.enter.prevent
          />
        </n-form-item>
        <!-- LOCALE -->
        <n-form-item path="locale" :label="$t('common.language')">
          <n-select
            v-model:value="segmentModel.locale"
            :options="localeOptions"
            :placeholder="$t('common.language')"
            :consistent-menu-width="false"
            :render-label="(o) => renderLanguageOptionLabel(localeOptions, o)"
            style="min-width: 200px"
            @keydown.enter.prevent
          />
        </n-form-item>
        <!-- HTML -->
        <n-form-item path="html" :label="$t('common.content')">
          <html-editor
            v-model:value="segmentModel.html"
            v-model:editor-mode="segmentModel.editorMode"
            :max-chars="1048576"
          />
        </n-form-item>
      </n-form>

      <button-shelf top-gap>
        <template #start>
          <n-button v-if="selectedSegmentId" secondary type="error" @click="handleDeleteClick">
            {{ $t('common.delete') }}
          </n-button>
        </template>
        <n-button secondary @click="handleCancelClick">{{ $t('common.cancel') }}</n-button>
        <n-button
          type="primary"
          :loading="loading"
          :disabled="!modelChanged"
          @click="handleSaveClick"
          >{{ $t('common.save') }}</n-button
        >
      </button-shelf>
    </div>
  </template>

  <n-empty v-else :description="$t('admin.segments.noSegment')" class="mt-lg">
    <template #icon>
      <n-icon :component="FileOpenIcon" />
    </template>
  </n-empty>
</template>
