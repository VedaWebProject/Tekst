<script setup lang="ts">
import { computed } from 'vue';
import { NAffix, NButton } from 'naive-ui';
import BrowseLocationControls from '@/components/browse/BrowseLocationControls.vue';
import BrowseLocationLabel from '@/components/browse/BrowseLocationLabel.vue';
import LayersRound from '@vicons/material/LayersRound';
import { useBrowseStore, useStateStore } from '@/stores';

const state = useStateStore();
const browse = useBrowseStore();

const showBrowseToolbar = computed(() => !!state.text);
</script>

<template>
  <div v-if="showBrowseToolbar" class="browse-toolbar-container">
    <n-affix :top="0" class="browse-toolbar-affix accent-color-bg">
      <div class="browse-toolbar">
        <BrowseLocationControls />
        <div class="browse-toolbar-spacer">
          <BrowseLocationLabel v-show="!state.smallScreen" class="browse-location-label" />
        </div>
        <n-button
          secondary
          size="large"
          :title="$t('browse.location.tipOpenDataLayerList')"
          color="#fffe"
          :focusable="false"
          @click="browse.showLayerToggleDrawer = true"
        >
          <template #icon>
            <LayersRound />
          </template>
        </n-button>
      </div>
    </n-affix>
  </div>
</template>

<style scoped>
.browse-toolbar-container {
  --browse-toolbar-height: 64px;
  height: var(--browse-toolbar-height);
  border-radius: var(--app-ui-border-radius);
  box-shadow: var(--app-ui-block-box-shadow);
}
.browse-toolbar-affix {
  width: 100%;
  max-width: var(--max-app-width);
  height: var(--browse-toolbar-height);
  border-radius: var(--app-ui-border-radius);
  box-shadow: var(--app-ui-block-box-shadow);
  transition: none;
}

.browse-toolbar-affix.n-affix--affixed {
  border-radius: unset;
  max-width: unset;
  width: 100vw;
  left: 0px;
  box-shadow: var(--app-ui-fixed-box-shadow);
  z-index: 2;
}

.browse-toolbar {
  height: var(--browse-toolbar-height);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24px;
  margin: 0 auto;
  padding: 0 var(--layout-padding);
}

.browse-toolbar-spacer {
  flex-grow: 2;
  overflow: hidden;
  text-overflow: ellipsis;
}

.browse-toolbar-affix.n-affix--affixed .browse-toolbar {
  max-width: var(--max-app-width);
}

.browse-toolbar .browse-location-label {
  display: none;
  opacity: 0.75;
}

.browse-toolbar-affix.n-affix--affixed .browse-location-label {
  display: initial;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
