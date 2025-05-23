<script setup lang="ts">
import { GET, type AnyContentRead, type AnyResourceRead } from '@/api';
import ContentContainerHeaderWidget from '@/components/browse/ContentContainerHeaderWidget.vue';
import contentComponents from '@/components/content/mappings';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import GenericModal from '@/components/generic/GenericModal.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import LocationLabel from '@/components/LocationLabel.vue';
import { $t } from '@/i18n';
import { useBrowseStore, useStateStore } from '@/stores';
import { NButton, NSpin } from 'naive-ui';
import { computed, ref } from 'vue';

import { BookIcon, MergeIcon, ResourceIcon } from '@/icons';
import { pickTranslation } from '@/utils';

const props = defineProps<{
  resource: AnyResourceRead;
  full?: boolean;
  showComments?: boolean;
}>();

const emit = defineEmits(['done']);

const state = useStateStore();
const browse = useBrowseStore();

const showModal = ref(false);
const loading = ref(false);
const contents = ref<AnyContentRead[]>([]);

const resourceTitle = computed(() => pickTranslation(props.resource.title, state.locale));

async function handleClick() {
  showModal.value = true;
  emit('done');
  loading.value = true;

  const { data: contentsData, error } = await GET('/browse/context', {
    params: {
      query: {
        res: props.resource.id,
        parent: browse.locationPath[props.resource.level - 1]?.id,
      },
    },
  });

  if (!error) {
    contents.value = contentsData;
  } else {
    showModal.value = false;
  }
  loading.value = false;
}
</script>

<template>
  <content-container-header-widget
    v-if="resource.config.general.enableContentContext && browse.level == resource.level"
    :title="$t('browse.contents.widgets.contextWidget.title')"
    :icon-component="MergeIcon"
    :full="full"
    @click="handleClick"
  />

  <generic-modal
    v-model:show="showModal"
    width="full"
    :title="resourceTitle"
    :icon="ResourceIcon"
    heading-level="2"
  >
    <icon-heading v-if="resource.level > 0" level="3" :icon="BookIcon">
      <location-label :max-level="resource.level - 1" />
    </icon-heading>

    <n-spin v-if="loading" class="centered-spinner" />

    <div v-else-if="contents.length" :dir="resource.config.general.rtl ? 'rtl' : undefined">
      <component
        :is="contentComponents[resource.resourceType]"
        :resource="{ ...resource, contents: contents }"
        :show-comments="showComments"
        :dir="resource.config.general.rtl ? 'rtl' : undefined"
      />
    </div>

    <span v-else class="translucent">
      {{ $t('browse.contents.widgets.contextWidget.noContext') }}
    </span>

    <button-shelf top-gap>
      <n-button type="primary" @click="() => (showModal = false)">
        {{ $t('common.close') }}
      </n-button>
    </button-shelf>
  </generic-modal>
</template>
