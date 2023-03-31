<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { NButton } from 'naive-ui';
import BrowseLocationControls from '@/components/browse/BrowseLocationControls.vue';
import BrowseLocationLabel from '@/components/browse/BrowseLocationLabel.vue';
import CompressRound from '@vicons/material/CompressRound';
import ExpandRound from '@vicons/material/ExpandRound';
import LayersRound from '@vicons/material/LayersRound';
import { useBrowseStore, useStateStore } from '@/stores';

const state = useStateStore();
const browse = useBrowseStore();

const affixRef = ref(null);

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
        <BrowseLocationLabel class="browse-location-label" />
      </div>

      <div class="browse-toolbar-end">
        <n-button
          :secondary="!browse.condensedView"
          :ghost="browse.condensedView"
          size="large"
          :title="$t('browse.toolbar.tipCondensedView')"
          color="#fff"
          :focusable="false"
          @click="browse.condensedView = !browse.condensedView"
        >
          <template #icon>
            <CompressRound v-if="!browse.condensedView" />
            <ExpandRound v-if="browse.condensedView" />
          </template>
        </n-button>

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
