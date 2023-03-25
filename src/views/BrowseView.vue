<script setup lang="ts">
import { watch, onMounted, type Component } from 'vue';
import BrowseLocationLabel from '@/components/browse/BrowseLocationLabel.vue';
import BrowseToolbar from '@/components/browse/BrowseToolbar.vue';
import { useStateStore, useBrowseStore, useMessagesStore } from '@/stores';
import { UnitsApi, LayersApi } from '@/openapi';
import { useRoute } from 'vue-router';
import PlaintextUnit from '@/components/units/PlaintextUnit.vue';
import UnitContainer from '@/components/browse/UnitContainer.vue';

const LAYER_TYPE_UNIT_COMPONENT_MAP: Record<string, Component> = {
  plaintext: PlaintextUnit,
};

const browse = useBrowseStore();
const state = useStateStore();
const messages = useMessagesStore();
const route = useRoute();

const layersApi = new LayersApi();
const unitsApi = new UnitsApi();

async function loadLayersData() {
  if (!state.text) return;
  Object.keys(browse.units).forEach((unitId) => (browse.units[unitId].loading = true));
  try {
    const data = await layersApi
      .findLayers({ textId: state.text.id })
      .then((response) => response.data);
    const layersData: Record<string, any> = {};
    data.forEach((u: Record<string, any>) => {
      layersData[u.id] = u;
    });
    browse.layers = layersData;
  } catch (e) {
    console.error(e);
    messages.error('Error loading data layers for this location');
  }
}

async function loadUnitsData() {
  if (!browse.nodePathHead) return;
  try {
    const data = await unitsApi
      .findUnits({ nodeId: [browse.nodePathHead.id] })
      .then((response) => response.data);
    const unitsData: Record<string, any> = {};
    data.forEach((u: Record<string, any>) => {
      // get layer this unit belongs to to add some of its data
      const l = browse.layers[u.layerId];
      unitsData[u.id] = {
        ...u,
        layerType: l?.layerType,
        layerTitle: l?.title,
      };
    });
    browse.units = unitsData;
  } catch (e) {
    console.error(e);
    messages.error('Error loading data layer units for this location');
  }
}

// load layers data on mount
onMounted(() => Object.keys(browse.layers).length == 0 && loadLayersData());

// load layers data on text change
watch(
  () => state.text,
  () => {
    route.name === 'browse' && loadLayersData();
  }
);

// load layers data on browse location change
watch(
  () => browse.nodePathHead,
  () => loadUnitsData()
);

// load units data on layers data change
watch(
  () => browse.layers,
  () => loadUnitsData()
);
</script>

<template>
  <div class="browse-heading-container">
    <h1>{{ state.text?.title }}</h1>
    <h2><BrowseLocationLabel /></h2>
  </div>

  <BrowseToolbar />

  <UnitContainer
    v-for="unit in browse.units"
    :key="unit.id"
    :title="unit.layerTitle"
    :loading="unit.loading"
  >
    <component :is="LAYER_TYPE_UNIT_COMPONENT_MAP[unit.layerType]" :dataId="unit.id" />
  </UnitContainer>
</template>

<style scoped>
.browse-heading-container {
  display: flex;
  flex-wrap: wrap;
  column-gap: 24px;
  row-gap: 12px;
  align-items: baseline;
  margin: 10px 0 24px 0;
}

.browse-heading-container > h1 {
  margin: 0;
}

.browse-heading-container > h2 {
  flex-grow: 2;
  overflow: hidden;
  text-overflow: ellipsis;
  opacity: 0.75;
  margin: 0;
  white-space: nowrap;
}
</style>
