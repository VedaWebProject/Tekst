<script setup lang="ts">
import { $t } from '@/i18n';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import WysiwygEditor from '@/components/WysiwygEditor.vue';
import { computed, ref } from 'vue';
import { NIcon, NButton, NSelect } from 'naive-ui';
import { usePlatformData } from '@/platformData';
import type { ClientSegmentUpdate } from '@/api';
import { localeProfiles } from '@/i18n';

import AddOutlined from '@vicons/material/AddOutlined';
import { useI18n } from 'vue-i18n';

const pf = usePlatformData();
const { locale } = useI18n();

const selectedSegmentId = ref<string | null>(null);
const segmentModel = ref<ClientSegmentUpdate & { id: string }>();
const segmentLocaleFlag = computed(() =>
  segmentModel.value?.locale ? localeProfiles[segmentModel.value.locale].icon : '🌐'
);
const segmentHeading = computed(() =>
  segmentModel.value
    ? segmentLocaleFlag.value + ' ' + (segmentModel.value.title || segmentModel.value.key)
    : ''
);

const segmentOptions = computed(() =>
  [...new Set(pf.pfData.value?.systemSegments.map((s) => s.key))].map((key) => {
    const groupSegments = pf.pfData.value?.systemSegments.filter((s) => s.key === key) || [];
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

function getSegmentModel(segmentId?: string) {
  if (!segmentId) {
    return {
      id: Math.random().toString(),
      key: '',
      title: '',
      locale: null,
      html: '',
    };
  } else {
    const selectedSegment = pf.pfData.value?.systemSegments.find((s) => s.id === segmentId);
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
}

function handleSelectSegment(id: string) {
  segmentModel.value = getSegmentModel(id);
}

function handleSaveClick() {
  //TODO
}

function handleDiscardClick() {
  selectedSegmentId.value = null;
  segmentModel.value = undefined;
}

function handleDeleteClick() {
  //TODO
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
    <n-button type="primary" :disabled="!!segmentModel" @click="handleAddSegmentClick">
      <template #icon>
        <n-icon :component="AddOutlined" />
      </template>
    </n-button>
  </div>

  <div v-if="segmentModel" class="content-block">
    <h3>{{ segmentModel.title ? segmentHeading : 'New Segment' }}</h3>
    <WysiwygEditor v-model:document="segmentModel.html" :document-id="segmentModel.id" />

    <div style="display: flex; gap: var(--layout-gap); margin-top: var(--layout-gap)">
      <n-button v-if="selectedSegmentId" secondary @click="handleDeleteClick"> Delete </n-button>
      <div style="flex-grow: 2"></div>
      <n-button secondary @click="handleDiscardClick"> Discard </n-button>
      <n-button type="primary" @click="handleSaveClick"> Save </n-button>
    </div>
  </div>
</template>
