<script setup lang="ts">
import { computed, type Component } from 'vue';
import BrowseLocationLabel from '@/components/browse/BrowseLocationLabel.vue';
import BrowseToolbar from '@/components/browse/BrowseToolbar.vue';
import { useStateStore, useBrowseStore } from '@/stores';
import PlaintextUnit from '@/components/units/PlaintextUnit.vue';
import UnitContainer from '@/components/browse/UnitContainer.vue';
import { NIcon } from 'naive-ui';
import FolderOffTwotone from '@vicons/material/FolderOffTwotone';
import LayerToggleDrawer from '@/components/browse/LayerToggleDrawer.vue';

const UNIT_COMPONENTS: Record<string, Component> = {
  plaintext: PlaintextUnit,
};

const browse = useBrowseStore();
const state = useStateStore();

const unitsExist = computed(() => {
  // count available units of ACTIVATED layers
  return browse.layers.filter((l) => l.active && l.unit).length > 0;
});
</script>

<template>
  <h1 class="browse-heading-title">{{ state.text?.title }}</h1>
  <h2 class="browse-heading-location"><BrowseLocationLabel /></h2>

  <BrowseToolbar />

  <UnitContainer
    v-for="layer in browse.layers"
    :key="`${layer.id}_${layer.active ? 'active' : 'inactive'}`"
    :title="layer.title"
    :loading="layer.loading"
    :active="!!(layer.active && layer.unit)"
    :meta="layer.meta"
    :layer-type="layer.layerType"
  >
    <component :is="UNIT_COMPONENTS[layer.layerType]" :data="layer.unit" />
  </UnitContainer>

  <div v-show="!unitsExist" class="browse-no-data">
    <n-icon size="48">
      <FolderOffTwotone />
    </n-icon>
    <div>{{ $t('browse.noData') }}</div>
  </div>

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

.browse-no-data {
  width: 512px;
  max-width: 100%;
  margin: 0 auto;
  padding: 3rem 0;
  text-align: center;
  opacity: 0.4;
  font-size: var(--app-ui-font-size-large);
  font-weight: var(--app-ui-font-weight-normal);
}
</style>
