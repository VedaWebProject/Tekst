<script setup lang="ts">
import { $t } from '@/i18n';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import WysiwygEditor from '@/components/WysiwygEditor.vue';
import { computed, ref } from 'vue';
import { NIcon, NButton, NSelect } from 'naive-ui';
import { usePlatformData } from '@/platformData';
import type { ClientSegmentRead } from '@/api';
import { localeProfiles } from '@/i18n';

import AddOutlined from '@vicons/material/AddOutlined';
import { useI18n } from 'vue-i18n';

const pf = usePlatformData();
const { locale } = useI18n();

const segment = ref<ClientSegmentRead>();
const segmentHeading = computed(() =>
  segment.value
    ? localeProfiles[segment.value.locale].icon + ' ' + (segment.value.title || segment.value.key)
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
        label: localeProfiles[s.locale].icon + ' ' + (s.title || s.key),
        value: s.id,
      })),
    };
  })
);

function handleAddSegmentClick() {
  // TODO
}

function handleSelectSegment(segmentId?: string) {
  if (!segmentId) return;
  const newSegment = pf.pfData.value?.systemSegments.find((s) => s.id === segmentId);
  if (!newSegment) {
    segment.value = undefined;
    return;
  }
  if (!segment.value) {
    segment.value = Object.assign({}, newSegment);
    return;
  }
  Object.assign(segment.value, newSegment);
}
</script>

<template>
  <h2>
    {{ $t('admin.system.segments.heading') }}
    <HelpButtonWidget help-key="adminSystemSegmentsView" />
  </h2>

  <div style="display: flex; gap: var(--layout-gap)">
    <n-select
      filterable
      :options="segmentOptions"
      placeholder="Select a segment"
      style="flex-grow: 2"
      @update:value="handleSelectSegment"
    />
    <n-button type="primary" @click="handleAddSegmentClick">
      <template #icon>
        <n-icon :component="AddOutlined" />
      </template>
    </n-button>
  </div>

  <div v-if="segment" class="content-block">
    <h3>{{ segmentHeading }}</h3>
    <WysiwygEditor v-model:document="segment.html" :document-id="segment.id" />
  </div>
</template>
