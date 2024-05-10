<script setup lang="ts">
import { computed, ref } from 'vue';
import { NAlert, NCollapse, NCollapseItem, NButton, NFormItem, NSelect } from 'naive-ui';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import ContentContainerHeaderWidget from '@/components/browse/ContentContainerHeaderWidget.vue';
import { useBrowseStore, useStateStore } from '@/stores';
import { GET, type AnyResourceRead, type LocationRead, type ResourceExportFormat } from '@/api';
import GenericModal from '@/components/generic/GenericModal.vue';
import { DownloadIcon } from '@/icons';
import LocationSelectForm from '@/forms/LocationSelectForm.vue';
import { $t } from '@/i18n';
import { useMessages } from '@/composables/messages';
import { getFullLocationLabel } from '@/utils';
import { useTasks } from '@/composables/tasks';

const allFormatOptions: { label: string; value: ResourceExportFormat }[] = [
  {
    label: 'JSON',
    value: 'json',
  },
  {
    label: 'Tekst-JSON',
    value: 'tekst-json',
  },
  {
    label: 'HTML',
    value: 'html',
  },
  {
    label: 'CSV',
    value: 'csv',
  },
  {
    label: 'Plain text',
    value: 'txt',
  },
];

const supportedExportFormats: Record<AnyResourceRead['resourceType'], ResourceExportFormat[]> = {
  plainText: ['json', 'tekst-json', 'csv'],
  richText: ['json', 'tekst-json', 'csv'],
  textAnnotation: ['json', 'tekst-json', 'csv'],
  audio: ['json', 'tekst-json', 'csv'],
  images: ['json', 'tekst-json', 'csv'],
};

const props = defineProps<{
  resource: AnyResourceRead;
}>();

const state = useStateStore();
const browse = useBrowseStore();
const { addTask, startTasksPolling } = useTasks();
const { message } = useMessages();

const showExportModal = ref(false);
const loadingExport = ref(false);

const format = ref<ResourceExportFormat>('json');
const formatOptions = computed(() =>
  allFormatOptions.filter((o) =>
    supportedExportFormats[props.resource.resourceType].includes(o.value)
  )
);
const formatInfoTitle = computed(
  () => allFormatOptions.find((o) => o.value === format.value)?.label
);
const formatInfoText = computed(() =>
  $t(`browse.contents.widgets.exportWidget.info.${format.value}`)
);

const fromLocationPath = ref<LocationRead[]>([]);
const toLocationPath = ref<LocationRead[]>([]);
const fromLocation = computed<LocationRead | undefined>(
  () => fromLocationPath.value[fromLocationPath.value.length - 1]
);
const toLocation = computed<LocationRead | undefined>(
  () => toLocationPath.value[toLocationPath.value.length - 1]
);

const fromLocationTitle = computed(() => {
  if (!fromLocationPath.value.length) {
    return $t('browse.contents.widgets.exportWidget.from') + ' ...';
  } else {
    return (
      $t('browse.contents.widgets.exportWidget.from') +
      ': ' +
      getFullLocationLabel(fromLocationPath.value, state.textLevelLabels, state.text)
    );
  }
});

const toLocationTitle = computed(() => {
  if (!toLocationPath.value.length) {
    return $t('browse.contents.widgets.exportWidget.to') + ' ...';
  } else {
    return (
      $t('browse.contents.widgets.exportWidget.to') +
      ': ' +
      getFullLocationLabel(toLocationPath.value, state.textLevelLabels, state.text)
    );
  }
});

const isLocationRangeValid = computed(
  () =>
    !fromLocation.value ||
    !toLocation.value ||
    fromLocation.value.position <= toLocation.value.position
);

const collapseExpandedModel = ref<string[]>([]);

async function startExport() {
  loadingExport.value = true;
  const { data, error } = await GET('/resources/{id}/export', {
    params: {
      path: { id: props.resource.id },
      query: {
        format: format.value,
        from: fromLocation.value?.id || null,
        to: toLocation.value?.id || null,
      },
    },
  });
  if (!error) {
    addTask(data);
    message.info($t('browse.contents.widgets.exportWidget.msgExportStarted'));
    startTasksPolling();
  }
  loadingExport.value = false;
  showExportModal.value = false;
}

async function selectFullLocationRange() {
  const { data, error } = await GET('/locations/first-last-paths', {
    params: { query: { txt: props.resource.textId, lvl: props.resource.level } },
  });
  if (!error) {
    fromLocationPath.value = data[0];
    toLocationPath.value = data[1];
    collapseExpandedModel.value = [];
  }
}

async function handleModalEnter() {
  if (browse.locationPath.length === props.resource.level + 1) {
    fromLocationPath.value = browse.locationPath;
    toLocationPath.value = browse.locationPath;
  } else {
    selectFullLocationRange();
  }
}

function handleModalLeave() {
  format.value = 'json';
  fromLocationPath.value = [];
  toLocationPath.value = [];
}
</script>

<template>
  <content-container-header-widget
    :title="$t('browse.contents.widgets.exportWidget.title')"
    :icon-component="DownloadIcon"
    @click="showExportModal = true"
  />

  <generic-modal
    v-model:show="showExportModal"
    :title="`${$t('browse.contents.widgets.exportWidget.title')}: ${resource.title}`"
    :icon="DownloadIcon"
    @after-enter="handleModalEnter"
    @after-leave="handleModalLeave"
  >
    <n-form-item :label="$t('browse.contents.widgets.exportWidget.format')">
      <n-select v-model:value="format" :options="formatOptions" />
    </n-form-item>

    <n-alert
      type="info"
      :title="formatInfoTitle"
      :closable="false"
      style="margin-bottom: var(--layout-gap)"
    >
      <span class="text-small">{{ formatInfoText }}</span>
    </n-alert>

    <n-collapse v-model:expanded-names="collapseExpandedModel">
      <n-collapse-item
        :title="fromLocationTitle"
        name="fromLocation"
        :disabled="!fromLocationPath.length"
      >
        <location-select-form v-model="fromLocationPath" :show-level-select="false" />
      </n-collapse-item>
      <n-collapse-item
        :title="toLocationTitle"
        name="toLocation"
        :disabled="!toLocationPath.length"
      >
        <location-select-form v-model="toLocationPath" :show-level-select="false" />
      </n-collapse-item>
    </n-collapse>

    <n-alert
      v-if="!isLocationRangeValid"
      type="error"
      :title="$t('general.error')"
      :closable="false"
      style="margin-top: var(--layout-gap)"
    >
      {{ $t('browse.contents.widgets.exportWidget.rangeError') }}
    </n-alert>

    <button-shelf top-gap>
      <template #start>
        <n-button
          secondary
          :disabled="
            loadingExport ||
            !isLocationRangeValid ||
            !fromLocationPath.length ||
            !toLocationPath.length
          "
          @click="selectFullLocationRange"
        >
          {{ $t('browse.contents.widgets.exportWidget.fullLocationRange') }}
        </n-button>
      </template>
      <n-button
        type="primary"
        :loading="loadingExport"
        :disabled="
          loadingExport ||
          !isLocationRangeValid ||
          !fromLocationPath.length ||
          !toLocationPath.length
        "
        @click="startExport"
      >
        {{ $t('general.exportAction') }}
      </n-button>
    </button-shelf>
  </generic-modal>
</template>
