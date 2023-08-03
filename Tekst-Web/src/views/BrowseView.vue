<script setup lang="ts">
import { computed } from 'vue';
import LocationLabel from '@/components/browse/LocationLabel.vue';
import BrowseToolbar from '@/components/browse/BrowseToolbar.vue';
import { useStateStore, useBrowseStore } from '@/stores';
import FolderOffTwotone from '@vicons/material/FolderOffTwotone';
import LayerToggleDrawer from '@/components/browse/LayerToggleDrawer.vue';
import UnitContainer from '@/components/browse/UnitContainer.vue';
import HugeLabeledIcon from '@/components/HugeLabeledIcon.vue';
import { useI18n } from 'vue-i18n';

const browse = useBrowseStore();
const state = useStateStore();
const { t } = useI18n({ useScope: 'global' });

const activeLayers = computed(() => {
  return browse.layers.filter((l) => l.active);
});
</script>

<template>
  <h1 class="browse-heading-title">{{ state.text?.title }}</h1>
  <h2 class="browse-heading-location"><LocationLabel /></h2>

  <BrowseToolbar />

  <template v-if="activeLayers.length">
    <UnitContainer
      v-for="layer in activeLayers"
      :key="layer.id"
      :loading="browse.loading"
      :layer="layer"
    />
  </template>

  <huge-labeled-icon v-else :message="t('browse.locationNoData')" :icon="FolderOffTwotone" />
  <LayerToggleDrawer v-model:show="browse.showLayerToggleDrawer" />
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
