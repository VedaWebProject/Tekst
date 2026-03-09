<script setup lang="ts">
import { GET, type AnyContentRead, type AnyResourceRead } from '@/api';
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

type AnyContentArchiveExtras = AnyContentRead & { createdAtStr?: string, distanceStr: string, distanceRel: number, };

const props = defineProps<{
  resource: AnyResourceRead;
  locationId: AnyContentRead['locationId'];
}>();

const state = useStateStore();
const { message } = useMessages();

const showModal = ref(false);
const loading = ref(false);
const selectedContent = ref<AnyContentArchiveExtras>();
const archivedContents = ref<AnyContentArchiveExtras[]>([]);
const title = ref($t('contents.archivedContentsTitle'));

function getContentLifetimeMs(contents: AnyContentRead[]){
  const byAge = contents.map(c => c.createdAt).sort((a, b) => b.localeCompare(a));
  return Math.abs(Math.ceil((new Date(byAge[byAge.length - 1]).getTime() - new Date(byAge[0]).getTime())));
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
    archivedContents.value = data.map((c) => ({
      ...c,
      createdAtStr: utcToDateTimeString(c.createdAt, state.locale),
      distanceStr: '0',
      distanceRel: 0,
    }));

    // compute time distances
    const maxTimespanMs = getContentLifetimeMs(data);
    archivedContents.value.forEach((c, i) => {
      if (i < archivedContents.value.length - 1) {
        const distanceMs = getContentLifetimeMs([c, data[i + 1]]);
        c.distanceStr = getTimeDistanceString(distanceMs);
        c.distanceRel = distanceMs / maxTimespanMs;
      };
    });
  } else {
    archivedContents.value = [];
    message.error($t('errors.unexpected'));
  }
  loading.value = false;
}

function handleItemClick(content: AnyContentArchiveExtras) {
  selectedContent.value = content;
  title.value = content.createdAtStr ?? $t('contents.archivedContentsTitle');
}

function handleBackToOverview() {
  selectedContent.value = undefined;
  title.value = $t('contents.archivedContentsTitle');
}

function cleanup() {
  selectedContent.value = undefined;
  archivedContents.value = [];
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
    <div v-if="selectedContent">
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
    <n-spin v-else-if="loading" class="centered-spin" />
    <template v-else-if="!selectedContent">
      <n-flex v-if="archivedContents?.length" vertical size="large">
        <template v-for="content in archivedContents" :key="content.id">
          <n-button secondary @click="handleItemClick(content)">
            {{ content.createdAtStr }}
          </n-button>
          <div v-if="content.distanceRel" class="time-gap text-tiny" :style="{lineHeight: (12 + (content.distanceRel * 120)) + 'px'}">
            {{ content.distanceStr }}
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
      <n-button secondary @click="showModal = false">
        {{ $t('common.close') }}
      </n-button>
    </button-shelf>
  </generic-modal>
</template>

<style scoped>
.time-gap {
  color: var(--primary-color);
  margin-left: 1rem;
  padding-left: .5rem;
  border-left: 1px dashed var(--primary-color);
}
</style>
