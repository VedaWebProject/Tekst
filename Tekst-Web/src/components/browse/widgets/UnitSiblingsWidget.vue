<script setup lang="ts">
import UnitContainerHeaderWidget from '@/components/browse/UnitContainerHeaderWidget.vue';
import MergeRound from '@vicons/material/MergeRound';
import { ref } from 'vue';
import { NModal, NButton, NSpin } from 'naive-ui';
import ButtonFooter from '@/components/ButtonFooter.vue';
import { GET } from '@/api';
import { useMessages } from '@/messages';
import { $t } from '@/i18n';
import unitComponents from '@/components/browse/units/mappings';
import LocationLabel from '@/components/browse/LocationLabel.vue';
import UnitHeaderWidgetBar from '@/components/browse/UnitHeaderWidgetBar.vue';
import { useBrowseStore } from '@/stores';

const props = defineProps<{
  layer: Record<string, any>;
}>();

const { message } = useMessages();
const browse = useBrowseStore();

const showModal = ref(false);
const loading = ref(false);
const units = ref<Record<string, any>[]>([]);

async function handleClick() {
  showModal.value = true;
  loading.value = true;

  const { data: unitsData, error } = await GET('/browse/unit-siblings', {
    params: {
      query: {
        layerId: props.layer.id,
        parentNodeId: browse.nodePath[props.layer.level - 1]?.id,
      },
    },
  });

  if (error) {
    message.error($t('errors.unexpected'), error);
    showModal.value = false;
    loading.value = false;
    return;
  } else {
    units.value = unitsData;
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

  <n-modal
    v-model:show="showModal"
    preset="card"
    class="tekst-modal tekst-modal-full"
    size="large"
    :bordered="false"
    :auto-focus="false"
    :closable="false"
    to="#app-container"
    embedded
  >
    <div class="header">
      <h2>{{ layer.title }}</h2>
      <UnitHeaderWidgetBar
        v-if="!loading && units.length"
        :layer="{ ...layer, units: units }"
        :show-deactivate-widget="false"
        :show-siblings-widget="false"
      />
    </div>

    <div class="parent-location"><LocationLabel :max-level="layer.level - 1" /></div>

    <n-spin v-if="loading" style="margin: 3rem 0 2rem 0; width: 100%" />

    <div v-else-if="units.length">
      <component
        :is="unitComponents[layer.layerType]"
        :layer="{ ...layer, units: units }"
        :layer-config="layer.config"
      />
    </div>

    <span v-else>{{ $t('errors.unexpected') }}</span>

    <ButtonFooter>
      <n-button type="primary" @click="() => (showModal = false)">
        {{ $t('general.closeAction') }}
      </n-button>
    </ButtonFooter>
  </n-modal>
</template>

<style scoped>
.header {
  display: flex;
  align-items: flex-start;
}

.header > h2 {
  flex-grow: 2;
}

.parent-location {
  font-size: var(--app-ui-font-size-large);
  opacity: 0.6;
  margin-bottom: 1rem;
}
</style>
