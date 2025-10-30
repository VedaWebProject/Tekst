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
import { infoSegmentFormRules, systemSegmentFormRules } from '@/forms/formRules';
import { $t, getLocaleProfile, renderLanguageOptionLabel } from '@/i18n';
import { AddIcon, FileOpenIcon, InfoIcon, SegmentsIcon } from '@/icons';
import { useStateStore } from '@/stores';
import { cloneDeep } from 'lodash-es';
import {
  NButton,
  NEmpty,
  NFlex,
  NForm,
  NFormItem,
  NIcon,
  NInput,
  NInputNumber,
  NSelect,
  useDialog,
  type FormInst,
  type InputInst,
} from 'naive-ui';
import { computed, nextTick, ref, watch } from 'vue';
import { useRoute } from 'vue-router';

const props = defineProps<{ segmentType: 'info' | 'system' }>();

const state = useStateStore();
const { loadPlatformData, getSegment } = usePlatformData();
const { message } = useMessages();
const dialog = useDialog();
const route = useRoute();

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
  props.segmentType == 'info'
    ? [...new Set(state.pf?.infoSegments.map((p) => p.key))].map((key) => {
        const groupSegments = state.pf?.infoSegments.filter((s) => s.key === key) || [];
        const currLocaleSegment =
          groupSegments.find((s) => s.locale === state.locale) ||
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
    : [...new Set(state.pf?.systemSegments.map((s) => s.key))].map((key) => {
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
    disabled: !!(
      props.segmentType == 'info' ? state.pf?.infoSegments : state.pf?.systemSegments
    )?.find(
      (p) =>
        p.locale === tlo.value &&
        p.key === segmentModel.value?.key &&
        p.id !== selectedSegmentId.value
    ),
  }))
);

const segmentSelectPlaceholder = computed(() => {
  if (props.segmentType === 'info') {
    return modelChanged.value ? $t('admin.infoPages.newPage') : $t('admin.infoPages.phSelectPage');
  } else {
    return modelChanged.value
      ? $t('admin.segments.newSegment')
      : $t('admin.segments.phSelectSegment');
  }
});

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

async function getSegmentModel(segmentId?: string): Promise<ClientSegmentUpdate> {
  if (!segmentId) {
    return {
      key: '',
      title: '',
      locale: '*',
      restriction: 'none',
      editorMode: 'wysiwyg',
      html: '',
    };
  } else {
    let selectedSegment = null;
    if (props.segmentType == 'info') {
      const selectedSegmentSignature = state.pf?.infoSegments.find((s) => s.id === segmentId);
      selectedSegment = await getSegment(
        selectedSegmentSignature?.key,
        selectedSegmentSignature?.locale || undefined
      );
    } else {
      selectedSegment = state.pf?.systemSegments.find((s) => s.id === segmentId);
    }
    if (!selectedSegment) {
      return await getSegmentModel();
    } else {
      return cloneDeep(selectedSegment);
    }
  }
}

async function handleChangeSegment(id?: string) {
  selectedSegmentId.value = id || null;
  segmentModel.value = await getSegmentModel(id);
  formRef.value?.restoreValidation();
  resetModelChanges();
  if (!id) nextTick(() => firstInputRef.value?.focus());
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
    clearForm();
    return;
  }
  dialog.warning({
    title: $t('common.warning'),
    content: $t('admin.segments.warnCancel'),
    positiveText: $t('common.yes'),
    negativeText: $t('common.no'),
    closable: false,
    ...dialogProps,
    onPositiveClick: clearForm,
  });
}

function clearForm() {
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
      clearForm();
      loadPlatformData();
    },
  });
}

/*
Reset view state when switching between system segments and info pages
(this is necessary because we're reusing this view component for both routes and the
component won't be re-rendered on route change)
*/
watch(
  () => route.name,
  () => {
    clearForm();
  }
);
</script>

<template>
  <icon-heading level="1" :icon="segmentType == 'info' ? InfoIcon : SegmentsIcon">
    {{ segmentType === 'info' ? $t('admin.infoPages.heading') : $t('admin.segments.heading') }}
    <help-button-widget
      :help-key="segmentType === 'info' ? 'adminInfoPagesView' : 'adminSegmentsView'"
    />
  </icon-heading>

  <n-flex :wrap="false">
    <n-select
      v-model:value="selectedSegmentId"
      filterable
      size="large"
      :disabled="modelChanged || !segmentOptions.length"
      :options="segmentOptions"
      :placeholder="segmentSelectPlaceholder"
      style="flex: 2"
      @update:value="handleChangeSegment"
    />
    <n-button
      type="primary"
      :disabled="modelChanged"
      size="large"
      @click="() => handleChangeSegment()"
    >
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
        :rules="segmentType === 'info' ? infoSegmentFormRules : systemSegmentFormRules"
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
        <n-form-item v-if="segmentType === 'info'" path="key" :label="$t('common.key')">
          <n-input
            v-model:value="segmentModel.key"
            type="text"
            :placeholder="$t('common.key')"
            @keydown.enter.prevent
          />
        </n-form-item>
        <n-form-item v-else path="key" :label="$t('common.type')">
          <n-select
            v-model:value="segmentModel.key"
            :options="systemSegmentKeyOptions"
            :consistent-menu-width="false"
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
            @keydown.enter.prevent
          />
        </n-form-item>

        <!-- RESTRICTION -->
        <n-form-item path="restriction" :label="$t('admin.segments.restriction.showTo')" required>
          <n-select
            v-model:value="segmentModel.restriction"
            :options="[
              {
                label: $t('admin.segments.restriction.none'),
                value: 'none',
              },
              {
                label: $t('admin.segments.restriction.user'),
                value: 'user',
              },
              {
                label: $t('admin.segments.restriction.superuser'),
                value: 'superuser',
              },
            ]"
            default-value="none"
            :consistent-menu-width="false"
            @keydown.enter.prevent
          />
        </n-form-item>

        <!-- SORT ORDER -->
        <n-form-item v-if="segmentType === 'info'" path="sortOrder" :label="$t('common.sortOrder')">
          <n-input-number
            v-model:value="segmentModel.sortOrder"
            :min="0"
            :max="1000"
            style="width: 100%"
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

  <n-empty
    v-else
    :description="
      segmentType === 'info' ? $t('admin.infoPages.noPage') : $t('admin.segments.noSegment')
    "
    class="mt-lg"
  >
    <template #icon>
      <n-icon :component="FileOpenIcon" />
    </template>
  </n-empty>
</template>
