<script setup lang="ts">
import { GET, POST, type AnyContentRead, type AnyResourceRead, type ContentArchiveSignature } from '@/api';
import contentComponents from '@/components/content/mappings';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import GenericModal from '@/components/generic/GenericModal.vue';
import { useMessages } from '@/composables/messages';
import { $t } from '@/i18n';
import { ArrowBackIcon, HistoryIcon, NoContentIcon } from '@/icons';
import { useStateStore } from '@/stores';
import { utcToDateTimeString } from '@/utils';
import { NButton, NEmpty, NFlex, NIcon, NSpin } from 'naive-ui';
import { ref } from 'vue';

type AnyContentArchiveItem = ContentArchiveSignature & { createdAtStr?: string, distanceMs: number, distanceStr: string, distanceRel: number, };

const props = defineProps<{
  resource: AnyResourceRead;
  locationId: AnyContentRead['locationId'];
}>();

const emit = defineEmits<{
  restore: [value: AnyContentRead]
}>()

const state = useStateStore();
const { message } = useMessages();

const showModal = ref(false);
const loading = ref(false);
const selectedContent = ref<AnyContentRead>();
const archiveItems = ref<AnyContentArchiveItem[]>([]);
const title = ref($t('contents.archivedContentsTitle'));

function getTsDistanceMs(utcStr1: string, utcStr2: string){
  return Math.ceil(Math.abs(new Date(utcStr1).getTime() - new Date(utcStr2).getTime()));
}

function getTimeDistanceString(ms: number) {
  const seconds = Math.floor(ms / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  const years = Math.floor(days / 365);
  const months = Math.floor((days % 365) / 30); // Remaining months
  const remainingDays = days % 30; // Remaining days

  const result = [];
  if (years > 0) result.push(years + ' ' + $t('common.years'));
  if (months > 0) result.push(months + ' ' + $t('common.months'));
  if (remainingDays > 0) result.push(remainingDays + ' ' + $t('common.days'));

  return result.join(', ');
}

function handleWidgetClick() {
  loading.value = true;
  showModal.value = true;
}

async function loadArchiveData() {
  loading.value = true;
  const { data, error } = await GET('/contents/archive', {
    params: {
      query: {
        resId: props.resource.id,
        locId: props.locationId,
      },
    },
  });
  if (!error) {
    archiveItems.value = data.map((a) => ({
      ...a,
      createdAtStr: utcToDateTimeString(a.createdAt, state.locale),
      distanceMs: 0,
      distanceStr: '0',
      distanceRel: 0,
    }));

    // compute time distances
    let maxDistanceMs = 0;
    archiveItems.value.forEach((a, i) => {
      if (i < archiveItems.value.length - 1) {
        a.distanceMs = getTsDistanceMs(a.createdAt, data[i + 1].createdAt);
        maxDistanceMs = a.distanceMs > maxDistanceMs ? a.distanceMs : maxDistanceMs;
        a.distanceStr = getTimeDistanceString(a.distanceMs);
      };
    });
    archiveItems.value.forEach((a) => {
      a.distanceRel = maxDistanceMs > 0 ? a.distanceMs / maxDistanceMs : 0;
    });
  } else {
    archiveItems.value = [];
    message.error($t('errors.unexpected'));
  }
  loading.value = false;
}

async function handleItemClick(archiveItem: AnyContentArchiveItem) {
  loading.value = true;
  const {data, error} = await GET('/contents/{id}', {params: {path: {id: archiveItem.id}}});
  if (!error){
    selectedContent.value = data;
    title.value = archiveItem.createdAtStr ?? $t('contents.archivedContentsTitle');
  }
  loading.value = false;
}

async function restoreArchivedContent(archivedContent: AnyContentRead) {
  if (!archivedContent.archived) return;
  loading.value = true;
  const {data, error} = await POST('/contents/{id}/restore', {params: {path: {id: archivedContent.id}}});
  if (!error){
    emit('restore', data);
    message.success($t('contents.msgRestored'));
  }
  loading.value = false;
  showModal.value = false
}

function handleBackToOverview() {
  selectedContent.value = undefined;
  title.value = $t('contents.archivedContentsTitle');
}

function cleanup() {
  selectedContent.value = undefined;
  archiveItems.value = [];
  title.value = $t('contents.archivedContentsTitle');
}
</script>

<template>
  <n-button v-bind="$attrs" @click.stop.prevent="handleWidgetClick">
    {{ $t('contents.archivedContentsTitle') }}
  </n-button>

  <generic-modal
    v-model:show="showModal"
    :title="title"
    :icon="HistoryIcon"
    width="wide"
    @after-enter="loadArchiveData"
    @after-leave="cleanup"
  >
    <n-spin v-if="loading" class="centered-spin" />
    <div v-else-if="selectedContent">
      <button-shelf>
        <template #start>
          <n-button text icon-placement="left" @click="handleBackToOverview">
            <template #icon>
              <n-icon :component="ArrowBackIcon" />
            </template>
            {{ $t('common.backToOverview') }}
          </n-button>
        </template>
      </button-shelf>
      <component
        :is="contentComponents[resource.resourceType]"
        :resource="{ ...resource, contents: [selectedContent] }"
        :focus-view="false"
        :show-comments="true"
        :dir="resource.config.general.rtl ? 'rtl' : undefined"
        class="my-lg"
      />
    </div>
    <template v-else-if="!selectedContent">
      <n-flex v-if="archiveItems?.length > 1" vertical size="large">
        <template v-for="item in archiveItems" :key="item.id">
          <n-button v-if="!item.archived" secondary disabled>
            {{ $t('common.today') }}
          </n-button>
          <n-button v-else secondary @click="handleItemClick(item)">
            {{ item.createdAtStr }}
          </n-button>
          <div v-if="item.distanceRel" class="time-gap translucent text-tiny" :style="{lineHeight: (12 + (item.distanceRel * 120)) + 'px'}">
            {{ item.distanceStr }}
          </div>
        </template>
      </n-flex>
      <n-empty v-else-if="!loading" :description="$t('contents.msgNoArchivedContents')">
        <template #icon>
          <n-icon :component="NoContentIcon" />
        </template>
      </n-empty>
    </template>

    <button-shelf class="mt-lg">
      <n-button v-if="!!selectedContent" secondary type="warning" @click="restoreArchivedContent(selectedContent)">
        {{ $t('contents.restore') }}
      </n-button>
      <n-button type="primary" @click="showModal = false">
        {{ $t('common.close') }}
      </n-button>
    </button-shelf>
  </generic-modal>
</template>

<style scoped>
.time-gap {
  margin-left: 1rem;
  padding-left: .5rem;
  border-left: 1px dashed var(--text-color);
}
</style>
