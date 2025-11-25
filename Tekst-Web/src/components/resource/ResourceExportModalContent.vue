<script setup lang="ts">
import { GET, type AnyResourceRead, type LocationRead, type ResourceExportFormat } from '@/api';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import { useMessages } from '@/composables/messages';
import { useTasks } from '@/composables/tasks';
import LocationSelectForm from '@/forms/LocationSelectForm.vue';
import { $t } from '@/i18n';
import { useAuthStore, useBrowseStore, useStateStore } from '@/stores';
import { getFullLocationLabel } from '@/utils';
import { NAlert, NButton, NCollapse, NCollapseItem, NFlex, NFormItem, NSelect } from 'naive-ui';
import { computed, onBeforeUnmount, onMounted, ref } from 'vue';

const allFormatOptions: { label: string; value: ResourceExportFormat; [key: string]: unknown }[] = [
  {
    label: 'JSON',
    value: 'json',
    restricted: false,
  },
  {
    label: 'Tekst-JSON',
    value: 'tekst-json',
    restricted: true,
  },
  {
    label: 'CSV',
    value: 'csv',
    restricted: false,
  },
];

const props = defineProps<{
  resource: AnyResourceRead;
}>();

const emit = defineEmits(['done']);

const state = useStateStore();
const auth = useAuthStore();
const browse = useBrowseStore();
const { addTask, startTasksPolling } = useTasks();
const { message } = useMessages();

const format = ref<ResourceExportFormat>('json');
const formatOptions = computed(() => allFormatOptions.filter((o) => !o.restricted || !!auth.user));

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
    return $t('common.from') + ' ...';
  } else {
    return (
      $t('common.from') +
      ': ' +
      getFullLocationLabel(fromLocationPath.value, state.textLevelLabels, state.text)
    );
  }
});

const toLocationTitle = computed(() => {
  if (!toLocationPath.value.length) {
    return $t('common.to') + ' ...';
  } else {
    return (
      $t('common.to') +
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
    message.info($t('common.msgExportStarted'));
    startTasksPolling();
  }
  emit('done');
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

onMounted(() => {
  if (browse.locationPath.length === props.resource.level + 1) {
    fromLocationPath.value = browse.locationPath;
    toLocationPath.value = browse.locationPath;
  } else {
    selectFullLocationRange();
  }
});

onBeforeUnmount(() => {
  format.value = 'json';
  fromLocationPath.value = [];
  toLocationPath.value = [];
});
</script>

<template>
  <div>
    <div class="gray-box">
      <n-form-item :label="$t('browse.contents.widgets.exportWidget.format')">
        <template #label>
          <n-flex align="center">
            <span>{{ $t('browse.contents.widgets.exportWidget.format') }}</span>
            <help-button-widget help-key="exportFormats" />
          </n-flex>
        </template>
        <n-select v-model:value="format" :options="formatOptions" />
      </n-form-item>

      <n-collapse v-model:expanded-names="collapseExpandedModel">
        <n-collapse-item
          :title="fromLocationTitle"
          name="fromLocation"
          :disabled="!fromLocationPath.length"
        >
          <location-select-form v-model="fromLocationPath" :allow-level-change="false" />
        </n-collapse-item>
        <n-collapse-item
          :title="toLocationTitle"
          name="toLocation"
          :disabled="!toLocationPath.length"
        >
          <location-select-form v-model="toLocationPath" :allow-level-change="false" />
        </n-collapse-item>
      </n-collapse>
    </div>

    <n-alert
      v-if="!isLocationRangeValid"
      type="error"
      :title="$t('common.error')"
      :closable="false"
      class="mt-lg"
    >
      {{ $t('browse.contents.widgets.exportWidget.rangeError') }}
    </n-alert>

    <button-shelf top-gap>
      <n-button
        secondary
        :disabled="!isLocationRangeValid || !fromLocationPath.length || !toLocationPath.length"
        @click="selectFullLocationRange"
      >
        {{ $t('browse.contents.widgets.exportWidget.fullLocationRange') }}
      </n-button>
      <n-button
        secondary
        type="primary"
        :disabled="!isLocationRangeValid || !fromLocationPath.length || !toLocationPath.length"
        @click="startExport"
      >
        {{ $t('common.export') }}
      </n-button>
    </button-shelf>
  </div>
</template>
