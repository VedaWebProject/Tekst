<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { NButton, NBadge } from 'naive-ui';
import BrowseLocationControls from '@/components/browse/BrowseLocationControls.vue';
import LocationLabel from '@/components/browse/LocationLabel.vue';
import { useBrowseStore, useStateStore } from '@/stores';

import CompressRound from '@vicons/material/CompressRound';
import ExpandRound from '@vicons/material/ExpandRound';
import LayersRound from '@vicons/material/LayersRound';

const state = useStateStore();
const browse = useBrowseStore();

const affixRef = ref(null);
const layerDrawerBadgeLabel = computed(
  () => browse.layers.filter((l) => l.active).length + '/' + browse.layers.length
);

onMounted(() => {
  if (affixRef.value) {
    new IntersectionObserver(
      ([e]) => e.target.classList.toggle('affixed', e.intersectionRatio < 1),
      { threshold: [1] }
    ).observe(affixRef.value);
  }
});
</script>

<template>
  <div ref="affixRef" class="browse-toolbar-container accent-color-bg">
    <div v-show="!!state.text" class="browse-toolbar">
      <BrowseLocationControls />

      <div v-show="!state.smallScreen" class="browse-toolbar-middle">
        <div class="browse-location-label">
          <LocationLabel />
        </div>
      </div>

      <div class="browse-toolbar-end">
        <n-button
          :secondary="!browse.reducedView"
          :ghost="browse.reducedView"
          size="large"
          :title="$t('browse.toolbar.tipReducedView')"
          color="#fff"
          :focusable="false"
          @click="browse.reducedView = !browse.reducedView"
        >
          <template #icon>
            <CompressRound v-if="!browse.reducedView" />
            <ExpandRound v-else />
          </template>
        </n-button>

        <n-badge
          :value="layerDrawerBadgeLabel"
          color="var(--accent-color-inverted-pastel)"
          :show="!!browse.layers.length"
        >
          <n-button
            secondary
            size="large"
            :title="$t('browse.toolbar.tipOpenDataLayerList')"
            color="#fff"
            :focusable="false"
            @click="browse.showLayerToggleDrawer = true"
          >
            <template #icon>
              <LayersRound />
            </template>
          </n-button>
        </n-badge>
      </div>
    </div>
  </div>
</template>

<style scoped>
.browse-toolbar-container {
  position: sticky;
  top: -1px;
  border-radius: var(--app-ui-border-radius);
  box-shadow: var(--app-ui-block-box-shadow);
  width: 100%;
  max-width: var(--max-app-width);
  padding: 12px 0;
  border-radius: var(--app-ui-border-radius);
  box-shadow: var(--app-ui-block-box-shadow);
  transition: none;
}

.browse-toolbar-container.affixed {
  border-top-left-radius: unset;
  border-top-right-radius: unset;
  max-width: unset;
  /* width: 100vw; */
  left: 0px;
  box-shadow: var(--app-ui-fixed-box-shadow);
  z-index: 2;
}

.browse-toolbar {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-around;
  align-items: center;
  gap: 12px;
  margin: 0 auto;
  padding: 0 12px;
}

.browse-toolbar-middle {
  flex-grow: 2;
  overflow: hidden;
  text-overflow: ellipsis;
}

.browse-toolbar-end {
  display: flex;
  gap: 12px;
}

.browse-toolbar-container.affixed .browse-toolbar {
  max-width: var(--max-app-width);
}

.browse-toolbar .browse-location-label {
  display: none;
  opacity: 0.75;
}

.browse-toolbar-container.affixed .browse-location-label {
  display: initial;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>

<style>
.n-badge > .n-badge-sup {
  color: var(--accent-color-inverted-dark);
}
</style>
