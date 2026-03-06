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

type AnyContentWithLocalArchiveTs = AnyContentRead & { archiveTsLocal?: string };

const props = defineProps<{
  resource: AnyResourceRead;
  locationId: AnyContentRead['locationId'];
}>();

const state = useStateStore();
const { message } = useMessages();

const showModal = ref(false);
const loading = ref(false);
const selectedContent = ref<AnyContentWithLocalArchiveTs>();
const archivedContents = ref<AnyContentWithLocalArchiveTs[]>([]);
const title = ref($t('contents.archivedContentsTitle'));

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
      archiveTsLocal: utcToDateTimeString(c.archiveTs, state.locale),
    }));
  } else {
    archivedContents.value = [];
    message.error($t('errors.unexpected'));
  }
  loading.value = false;
}

function handleItemClick(content: AnyContentWithLocalArchiveTs) {
  selectedContent.value = content;
  title.value = content.archiveTsLocal ?? $t('contents.archivedContentsTitle');
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
        <n-button
          v-for="content in archivedContents"
          :key="content.id"
          secondary
          @click="handleItemClick(content)"
        >
          {{ content.archiveTsLocal }}
        </n-button>
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
