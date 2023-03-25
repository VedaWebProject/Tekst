<script setup lang="ts">
import { onMounted, type Component } from 'vue';
import BrowseLocationLabel from '@/components/browse/BrowseLocationLabel.vue';
import BrowseToolbar from '@/components/browse/BrowseToolbar.vue';
import { useStateStore, useBrowseStore } from '@/stores';
import PlaintextUnit from '@/components/units/PlaintextUnit.vue';
import UnitContainer from '@/components/browse/UnitContainer.vue';

const UNIT_COMPONENTS: Record<string, Component> = {
  plaintext: PlaintextUnit,
};

const browse = useBrowseStore();
const state = useStateStore();

// load layers data on mount
onMounted(() => Object.keys(browse.layers).length == 0 && browse.loadLayersData());
</script>

<template>
  <h1 class="browse-heading-title">{{ state.text?.title }}</h1>
  <h2 class="browse-heading-location"><BrowseLocationLabel /></h2>

  <BrowseToolbar />

  <UnitContainer
    v-for="unit in browse.units"
    :key="unit.id"
    :title="unit.layerTitle"
    :loading="unit.loading"
  >
    <component :is="UNIT_COMPONENTS[unit.layerType]" :dataId="unit.id" />
  </UnitContainer>
</template>

<style scoped>
.browse-heading-title {
  margin: 0;
}

.browse-heading-location {
  flex-grow: 2;
  overflow: hidden;
  text-overflow: ellipsis;
  opacity: 0.6;
  white-space: nowrap;
  margin-top: 12px;
}
</style>
