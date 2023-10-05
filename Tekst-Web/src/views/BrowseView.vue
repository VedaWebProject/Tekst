<script setup lang="ts">
import { computed } from 'vue';
import LocationLabel from '@/components/browse/LocationLabel.vue';
import BrowseToolbar from '@/components/browse/BrowseToolbar.vue';
import { useBrowseStore } from '@/stores';
import LayerToggleDrawer from '@/components/browse/LayerToggleDrawer.vue';
import UnitContainer from '@/components/browse/UnitContainer.vue';
import HugeLabeledIcon from '@/components/HugeLabeledIcon.vue';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';

import FolderOffTwotone from '@vicons/material/FolderOffTwotone';
import HourglassTopTwotone from '@vicons/material/HourglassTopTwotone';

const browse = useBrowseStore();

const activeLayers = computed(() => {
  return browse.layers.filter((l) => l.active);
});
</script>

<template>
  <h1>
    <LocationLabel />&nbsp;
    <HelpButtonWidget />
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

  <huge-labeled-icon
    v-else-if="browse.loading"
    :message="$t('init.loading')"
    :icon="HourglassTopTwotone"
  />
  <huge-labeled-icon v-else :message="$t('browse.locationNoData')" :icon="FolderOffTwotone" />
  <LayerToggleDrawer v-model:show="browse.showLayerToggleDrawer" />
</template>

<style scoped>
.browse-heading-location.smallscreen {
  font-size: 1.3rem;
}
</style>
