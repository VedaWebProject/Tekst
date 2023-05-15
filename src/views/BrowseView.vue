<script setup lang="ts">
import { computed } from 'vue';
import BrowseLocationLabel from '@/components/browse/BrowseLocationLabel.vue';
import BrowseToolbar from '@/components/browse/BrowseToolbar.vue';
import { useStateStore, useBrowseStore } from '@/stores';
import { NSpin } from 'naive-ui';
import FolderOffTwotone from '@vicons/material/FolderOffTwotone';
import LayerToggleDrawer from '@/components/browse/LayerToggleDrawer.vue';
import UnitContainer from '@/components/browse/UnitContainer.vue';
import HugeLabeledIcon from '@/components/HugeLabeledIcon.vue';

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
    :loading="browse.loading"
    :layer="layer"
  />

  <huge-labeled-icon
    v-show="!unitsExist && !browse.loading"
    :message="$t('browse.noData')"
    :icon="FolderOffTwotone"
  />

  <n-spin
    v-if="!unitsExist && browse.loading"
    style="margin: 3rem auto 2rem auto; display: flex"
    :description="$t('init.loading')"
  ></n-spin>

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
