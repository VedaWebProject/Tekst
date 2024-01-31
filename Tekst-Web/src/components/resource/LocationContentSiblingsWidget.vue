<script setup lang="ts">
import ContentContainerHeaderWidget from '@/components/browse/ContentContainerHeaderWidget.vue';
import { ref } from 'vue';
import { NButton, NSpin } from 'naive-ui';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import { GET, type AnyContentRead, type AnyResourceRead } from '@/api';
import { useMessages } from '@/composables/messages';
import { $t } from '@/i18n';
import contentComponents from '@/components/content/mappings';
import LocationLabel from '@/components/LocationLabel.vue';
import { useBrowseStore } from '@/stores';
import GenericModal from '@/components/generic/GenericModal.vue';
import IconHeading from '@/components/generic/IconHeading.vue';

import { MergeIcon, BookIcon, ResourceIcon } from '@/icons';

const props = defineProps<{
  resource: AnyResourceRead;
}>();

const { message } = useMessages();
const browse = useBrowseStore();

const showModal = ref(false);
const loading = ref(false);
const contents = ref<AnyContentRead[]>([]);

async function handleClick() {
  showModal.value = true;
  loading.value = true;

  const { data: contentsData, error } = await GET('/browse/content-siblings', {
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
    message.error($t('errors.unexpected'), error);
    showModal.value = false;
  }
  loading.value = false;
}
</script>

<template>
  <content-container-header-widget
    :title="$t('browse.contents.widgets.siblingsWidget.title')"
    :icon-component="MergeIcon"
    @click="handleClick"
  />

  <generic-modal
    v-model:show="showModal"
    width="wide"
    :title="resource.title"
    :icon="ResourceIcon"
    heading-level="2"
  >
    <icon-heading v-if="resource.level > 0" level="3" :icon="BookIcon">
      <location-label :max-level="resource.level - 1" />
    </icon-heading>

    <n-spin v-if="loading" style="margin: 3rem 0 2rem 0; width: 100%" />

    <div v-else-if="contents.length">
      <component
        :is="contentComponents[resource.resourceType]"
        :resource="{ ...resource, contents: contents }"
      />
    </div>

    <span v-else>{{ $t('errors.unexpected') }}</span>

    <button-shelf top-gap>
      <n-button type="primary" @click="() => (showModal = false)">
        {{ $t('general.closeAction') }}
      </n-button>
    </button-shelf>
  </generic-modal>
</template>

<style scoped>
.parent-location {
  font-size: var(--app-ui-font-size-large);
  opacity: 0.6;
  margin-bottom: 1rem;
}
</style>
