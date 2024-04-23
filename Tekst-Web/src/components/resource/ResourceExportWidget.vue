<script setup lang="ts">
import { computed, ref } from 'vue';
import { NCollapse, NCollapseItem, NButton, NFormItem, NSelect } from 'naive-ui';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import ContentContainerHeaderWidget from '@/components/browse/ContentContainerHeaderWidget.vue';
import { useStateStore } from '@/stores';
import {
  GET,
  type AnyResourceRead,
  type LocationRead,
  type ResourceExportFormat,
  saveDownload,
} from '@/api';
import GenericModal from '@/components/generic/GenericModal.vue';
import { DownloadIcon } from '@/icons';
import LocationSelectForm from '@/forms/LocationSelectForm.vue';
import { $t } from '@/i18n';
import { useMessages } from '@/composables/messages';

const props = defineProps<{
  resource: AnyResourceRead;
}>();

const state = useStateStore();
const { message } = useMessages();

const showExportModal = ref(false);
const loadingExport = ref(false);

const format = ref<ResourceExportFormat>('json');
const formatOptions = [
  {
    label: 'JSON',
    value: 'json',
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

const fromLocationPath = ref<LocationRead[]>([]);
const toLocationPath = ref<LocationRead[]>([]);

const fromLocationTitle = computed(() => {
  if (!fromLocationPath.value.length) {
    return $t('browse.contents.widgets.exportWidget.from') + ' ...';
  } else {
    return (
      $t('browse.contents.widgets.exportWidget.from') +
      ': ' +
      state.textLevelLabels[props.resource.level] +
      ' "' +
      fromLocationPath.value[fromLocationPath.value.length - 1].label +
      '"'
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
      state.textLevelLabels[props.resource.level] +
      ' "' +
      toLocationPath.value[toLocationPath.value.length - 1].label +
      '"'
    );
  }
});

async function handleExportClick() {
  loadingExport.value = true;
  const { response, error } = await GET('/resources/{id}/export', {
    params: {
      path: { id: props.resource.id },
      query: {
        format: format.value,
        from: fromLocationPath.value[fromLocationPath.value.length - 1].id,
        to: toLocationPath.value[toLocationPath.value.length - 1].id,
      },
    },
    parseAs: 'blob',
  });
  if (!error) {
    const filename =
      response.clone().headers.get('content-disposition')?.split('filename=')[1] ||
      `${state.text?.slug || 'text'}_${props.resource.id}_export.${format.value}`;
    message.info($t('general.downloadSaved', { filename }));
    saveDownload(await response.blob(), filename);
  }
  loadingExport.value = false;
  showExportModal.value = false;
}

async function handleModalEnter() {
  const { data, error } = await GET('/locations/first-last-paths', {
    params: { query: { txt: props.resource.textId, lvl: props.resource.level } },
  });
  if (!error) {
    fromLocationPath.value = data[0];
    toLocationPath.value = data[1];
  }
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
  >
    <n-form-item :label="$t('browse.contents.widgets.exportWidget.format')">
      <n-select v-model:value="format" :options="formatOptions" />
    </n-form-item>

    <n-collapse display-directive="show">
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

    <button-shelf top-gap>
      <n-button
        type="primary"
        :loading="loadingExport"
        :disabled="loadingExport"
        @click="handleExportClick"
      >
        {{ $t('general.exportAction') }}
      </n-button>
    </button-shelf>
  </generic-modal>
</template>
