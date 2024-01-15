<script setup lang="ts">
import UnitContainerHeaderWidget from '@/components/browse/UnitContainerHeaderWidget.vue';
import MergeRound from '@vicons/material/MergeRound';
import { ref } from 'vue';
import { NButton, NSpin } from 'naive-ui';
import ButtonShelf from '@/components/ButtonShelf.vue';
import { GET, type AnyUnitRead, type AnyResourceRead } from '@/api';
import { useMessages } from '@/messages';
import { $t } from '@/i18n';
import unitComponents from '@/components/browse/units/mappings';
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
const units = ref<AnyUnitRead[]>([]);

async function handleClick() {
  showModal.value = true;
  loading.value = true;

  const { data: unitsData, error } = await GET('/browse/unit-siblings', {
    params: {
      query: {
        res: props.resource.id,
        parent: browse.nodePath[props.resource.level - 1]?.id,
      },
    },
  });

  if (!error) {
    units.value = unitsData;
  } else {
    message.error($t('errors.unexpected'), error);
    showModal.value = false;
  }
  loading.value = false;
}
</script>

<template>
  <UnitContainerHeaderWidget
    :title="$t('browse.units.widgets.siblingsWidget.title')"
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

    <div v-else-if="units.length">
      <component
        :is="unitComponents[resource.resourceType]"
        :resource="{ ...resource, units: units }"
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
