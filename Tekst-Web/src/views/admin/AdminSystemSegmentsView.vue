<script setup lang="ts">
import { $t } from '@/i18n';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import WysiwygEditor from '@/components/WysiwygEditor.vue';
import { computed, ref } from 'vue';
import { NIcon, NButton, NSelect, NForm, NFormItem, NInput, type FormInst } from 'naive-ui';
import { usePlatformData } from '@/platformData';
import { PATCH, type ClientSegmentUpdate, POST, type ClientSegmentCreate, DELETE } from '@/api';
import { localeProfiles } from '@/i18n';
import HugeLabeledIcon from '@/components/HugeLabeledIcon.vue';

import { useI18n } from 'vue-i18n';
import { useModelChanges } from '@/modelChanges';
import { useMessages } from '@/messages';
import { systemSegmentFormRules } from '@/formRules';

import AddOutlined from '@vicons/material/AddOutlined';
import FileOpenOutlined from '@vicons/material/FileOpenOutlined';
import DeleteOutlined from '@vicons/material/DeleteOutlined';

const { pfData, loadPlatformData } = usePlatformData();
const { locale } = useI18n();
const { message } = useMessages();

const loading = ref(false);
const formRef = ref<FormInst | null>(null);
const selectedSegmentId = ref<string | null>(null);
const segmentModel = ref<ClientSegmentUpdate>();

const {
  changed: modelChanged,
  reset: resetModelChanges,
  getChanges: getModelChanges,
} = useModelChanges(segmentModel);

const segmentLocaleFlag = computed(() =>
  segmentModel.value?.locale ? localeProfiles[segmentModel.value.locale].icon : '🌐'
);
const segmentHeading = computed(() =>
  segmentModel.value
    ? segmentLocaleFlag.value + ' ' + (segmentModel.value.title || segmentModel.value.key)
    : ''
);

const segmentOptions = computed(() =>
  [...new Set(pfData.value?.systemSegments.map((s) => s.key))].map((key) => {
    const groupSegments = pfData.value?.systemSegments.filter((s) => s.key === key) || [];
    const currLocaleSegment =
      groupSegments.find((s) => s.locale === locale.value) ||
      groupSegments.find((s) => s.locale === 'enUS') ||
      groupSegments[0];
    return {
      type: 'group',
      label: currLocaleSegment.title || currLocaleSegment.key,
      key,
      children: groupSegments.map((s) => ({
        label: (s.locale ? localeProfiles[s.locale].icon : '🌐') + ' ' + (s.title || s.key),
        value: s.id,
      })),
    };
  })
);

const segmentLocaleOptions = computed(() =>
  Object.keys(localeProfiles).map((l) => ({
    label: `${localeProfiles[l].icon} ${localeProfiles[l].displayFull}`,
    value: l,
    disabled: !!pfData.value?.systemSegments.find(
      (s) => s.locale === l && s.key === segmentModel.value?.key && s.id !== selectedSegmentId.value
    ),
  }))
);

const systemSegmentKeys = [
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

function getSegmentModel(segmentId?: string) {
  if (!segmentId) {
    return {
      key: undefined,
      title: '',
      locale: undefined,
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
    message.success('SAVED');
    selectedSegmentId.value = data.id;
    segmentModel.value = data;
    resetModelChanges();
    loadPlatformData();
  } else {
    message.error('ERROR', error.detail?.toString());
  }
}

async function createSegment() {
  const { data, error } = await POST('/platform/segments', {
    body: getModelChanges() as ClientSegmentCreate,
  });
  if (!error) {
    message.success('Created');
    selectedSegmentId.value = data.id;
    segmentModel.value = data;
    resetModelChanges();
    loadPlatformData();
  } else {
    message.error('ERROR', error);
  }
}

function resetForm() {
  selectedSegmentId.value = null;
  segmentModel.value = undefined;
  resetModelChanges();
  formRef.value?.restoreValidation();
}

async function handleDeleteClick() {
  if (!selectedSegmentId.value) return;
  const { error } = await DELETE('/platform/segments/{id}', {
    params: { path: { id: selectedSegmentId.value } },
  });
  if (!error) {
    message.success('Deleted: ' + segmentModel.value?.title);
  } else {
    message.error('Error deleting segment!');
  }
  resetForm();
  loadPlatformData();
}
</script>

<template>
  <h2>
    {{ $t('admin.system.segments.heading') }}
    <HelpButtonWidget help-key="adminSystemSegmentsView" />
  </h2>

  <div style="display: flex; gap: var(--layout-gap)">
    <n-select
      v-model:value="selectedSegmentId"
      filterable
      :options="segmentOptions"
      placeholder="Select a segment"
      style="flex-grow: 2"
      @update:value="handleSelectSegment"
    />
    <n-button v-if="selectedSegmentId" secondary @click="handleDeleteClick">
      <template #icon>
        <n-icon :component="DeleteOutlined" />
      </template>
    </n-button>
    <n-button type="primary" :disabled="modelChanged" @click="handleAddSegmentClick">
      <template #icon>
        <n-icon :component="AddOutlined" />
      </template>
    </n-button>
  </div>

  <div v-if="segmentModel" class="content-block">
    <h3>{{ segmentModel.title ? segmentHeading : 'Untitled' }}</h3>

    <n-form
      ref="formRef"
      :model="segmentModel"
      :rules="systemSegmentFormRules"
      label-placement="top"
      label-width="auto"
      require-mark-placement="right-hanging"
    >
      <!-- TITLE -->
      <n-form-item path="title" :label="$t('models.segment.title')">
        <n-input
          v-model:value="segmentModel.title"
          type="text"
          :placeholder="$t('models.segment.title')"
          :disabled="loading"
          @keydown.enter.prevent
        />
      </n-form-item>
      <!-- KEY -->
      <n-form-item path="key" :label="$t('models.segment.key')" required>
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
      <n-form-item :label="$t('models.segment.locale')">
        <n-select
          v-model:value="segmentModel.locale"
          :options="segmentLocaleOptions"
          :placeholder="$t('general.language')"
          :consistent-menu-width="false"
          style="min-width: 200px"
          @keydown.enter.prevent
        />
      </n-form-item>
      <!-- HTML -->
      <n-form-item path="html" :label="$t('models.segment.html')" required>
        <WysiwygEditor v-model:value="segmentModel.html" toolbar-size="medium" />
      </n-form-item>
    </n-form>

    <div style="display: flex; gap: var(--layout-gap); justify-content: end">
      <n-button secondary @click="resetForm"> Cancel </n-button>
      <n-button type="primary" :disabled="!modelChanged" @click="handleSaveClick"> Save </n-button>
    </div>
  </div>

  <HugeLabeledIcon
    v-else
    message="Please select a segment from the list or create a new one!"
    :icon="FileOpenOutlined"
  />
</template>
