<script setup lang="ts">
import UnitContainerHeaderWidget from '@/components/browse/UnitContainerHeaderWidget.vue';
import MergeRound from '@vicons/material/MergeRound';
import { ref } from 'vue';
import { NModal, NButton, NSpin } from 'naive-ui';
import ModalButtonFooter from '@/components/ModalButtonFooter.vue';
import { useApi } from '@/api';
import { useMessages } from '@/messages';
import { useI18n } from 'vue-i18n';
import unitComponents from '@/components/browse/units/mappings';
import BrowseLocationLabel from '@/components/browse/BrowseLocationLabel.vue';

const props = defineProps<{
  layer: Record<string, any>;
}>();

const { unitsApi } = useApi();
const { message } = useMessages();
const { t } = useI18n({ useScope: 'global' });

const showModal = ref(false);
const loading = ref(false);
const units = ref<Record<string, any>[]>([]);

async function handleClick() {
  showModal.value = true;
  loading.value = true;
  try {
    units.value = (await unitsApi.getSiblings({ unitId: props.layer.unit.id })).data;
  } catch {
    message.error(t('errors.unexpected'));
    showModal.value = false;
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <UnitContainerHeaderWidget
    :title="$t('browse.units.widgets.mergeWidget.title')"
    :iconComponent="MergeRound"
    @click="handleClick"
  />

  <n-modal
    v-model:show="showModal"
    preset="card"
    class="tekst-modal tekst-modal-large"
    size="large"
    :bordered="false"
    :auto-focus="false"
    :closable="false"
    to="#app-container"
    embedded
  >
    <h2>{{ layer.title }}</h2>
    <h3><BrowseLocationLabel :maxLevel="layer.level" /></h3>

    <div v-if="!loading && units.length">
      <component
        v-for="unit in units"
        :key="unit.id"
        :is="unitComponents[layer.layerType]"
        :layer="{ ...layer, unit: unit }"
        :layer-config="layer.config"
        style="margin-top: 0.5rem"
      />
    </div>

    <n-spin v-else style="margin: 3rem 0 2rem 0; width: 100%" />

    <ModalButtonFooter>
      <n-button type="primary" @click="() => (showModal = false)">
        {{ $t('general.closeAction') }}
      </n-button>
    </ModalButtonFooter>
  </n-modal>
</template>
