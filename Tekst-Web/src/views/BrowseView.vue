<script setup lang="ts">
import { computed } from 'vue';
import LocationLabel from '@/components/browse/LocationLabel.vue';
import BrowseToolbar from '@/components/browse/BrowseToolbar.vue';
import { useBrowseStore, useStateStore } from '@/stores';
import FolderOffTwotone from '@vicons/material/FolderOffTwotone';
import LayerToggleDrawer from '@/components/browse/LayerToggleDrawer.vue';
import UnitContainer from '@/components/browse/UnitContainer.vue';
import HugeLabeledIcon from '@/components/HugeLabeledIcon.vue';

const state = useStateStore();
const browse = useBrowseStore();

const activeLayers = computed(() => {
  return browse.layers.filter((l) => l.active);
});
</script>

<template>
  <h1 class="browse-heading-location" :class="state.smallScreen && 'smallscreen'">
    <LocationLabel />
  </h1>

  <BrowseToolbar />

  <template v-if="activeLayers.length">
    <UnitContainer
      v-for="layer in activeLayers"
      :key="layer.id"
      :loading="browse.loading"
      :layer="layer"
    />
  </template>

  <huge-labeled-icon v-else :message="$t('browse.locationNoData')" :icon="FolderOffTwotone" />
  <LayerToggleDrawer v-model:show="browse.showLayerToggleDrawer" />
</template>

<style scoped>
.browse-heading-title {
  margin: 0;
}

.browse-heading-location.smallscreen {
  font-size: 1.3rem;
}
</style>
