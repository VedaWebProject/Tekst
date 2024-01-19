<script setup lang="ts">
import ContentContainerHeaderWidget from '@/components/browse/ContentContainerHeaderWidget.vue';
import MergeRound from '@vicons/material/MergeRound';
import { ref } from 'vue';
import { NButton, NSpin } from 'naive-ui';
import ButtonShelf from '@/components/ButtonShelf.vue';
import { GET, type AnyContentRead, type AnyResourceRead } from '@/api';
import { useMessages } from '@/messages';
import { $t } from '@/i18n';
import contentComponents from '@/components/browse/contents/mappings';
import LocationLabel from '@/components/browse/LocationLabel.vue';
import { useBrowseStore } from '@/stores';
import GenericModal from '@/components/GenericModal.vue';
import IconHeading from '@/components/typography/IconHeading.vue';

import MenuBookOutlined from '@vicons/material/MenuBookOutlined';
import MergeOutlined from '@vicons/material/MergeOutlined';

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
  <ContentContainerHeaderWidget
    :title="$t('browse.contents.widgets.siblingsWidget.title')"
    :icon-component="MergeRound"
    @click="handleClick"
  />

  <GenericModal
    v-model:show="showModal"
    width="wide"
    :title="resource.title"
    :icon="MergeOutlined"
    heading-level="2"
  >
    <IconHeading v-if="resource.level > 0" level="3" :icon="MenuBookOutlined">
      <LocationLabel :max-level="resource.level - 1" />
    </IconHeading>

    <n-spin v-if="loading" style="margin: 3rem 0 2rem 0; width: 100%" />

    <div v-else-if="contents.length">
      <component
        :is="contentComponents[resource.resourceType]"
        :resource="{ ...resource, contents: contents }"
      />
    </div>

    <span v-else>{{ $t('errors.unexpected') }}</span>

    <ButtonShelf top-gap>
      <n-button type="primary" @click="() => (showModal = false)">
        {{ $t('general.closeAction') }}
      </n-button>
    </ButtonShelf>
  </GenericModal>
</template>

<style scoped>
.parent-location {
  font-size: var(--app-ui-font-size-large);
  opacity: 0.6;
  margin-bottom: 1rem;
}
</style>
