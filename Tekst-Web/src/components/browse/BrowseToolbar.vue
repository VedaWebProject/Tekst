<script setup lang="ts">
import { ref, onMounted, computed, nextTick } from 'vue';
import { NButton, NBadge, NIcon, NFlex } from 'naive-ui';
import BrowseLocationControls from '@/components/browse/BrowseLocationControls.vue';
import LocationLabel from '@/components/LocationLabel.vue';
import { useBrowseStore, useStateStore, useThemeStore, useSearchStore } from '@/stores';
import BrowseSearchResultsToolbar from '@/components/browse/BrowseSearchResultsToolbar.vue';
import { CompressIcon, ExpandIcon, ResourceIcon } from '@/icons';

const state = useStateStore();
const browse = useBrowseStore();
const search = useSearchStore();
const theme = useThemeStore();

const affixRef = ref();
const resourcesCount = computed(
  () => browse.resourcesCategorized.map((c) => c.resources).flat().length
);
const activeResourcesCount = computed(
  () =>
    browse.resourcesCategorized
      .map((c) => c.resources)
      .flat()
      .filter((r) => r.active).length
);
const resourceDrawerBadgeLabel = computed(() =>
  resourcesCount.value ? activeResourcesCount.value + '/' + resourcesCount.value : '...'
);

onMounted(() => {
  nextTick(() => {
    if (affixRef.value) {
      new IntersectionObserver(
        ([e]) => e.target.classList.toggle('affixed', e.intersectionRatio < 1),
        { threshold: [1] }
      ).observe(affixRef.value);
    }
  });
});

const buttonSize = computed(() => (state.smallScreen ? 'small' : 'large'));
</script>

<template>
  <div ref="affixRef" :wrap="false" class="browse-toolbar-container mb-lg">
    <browse-search-results-toolbar
      v-if="search.browseHits"
      :small-screen="state.smallScreen"
      :button-size="buttonSize"
    />
    <n-flex
      v-show="!!state.text"
      :wrap="false"
      justify="space-between"
      align="center"
      class="browse-toolbar accent-color-bg"
    >
      <browse-location-controls
        :button-size="buttonSize"
        @navigate="() => browse.setResourcesActiveState()"
      />

      <div class="browse-toolbar-middle">
        <div v-show="!state.smallScreen" class="browse-location-label">
          <location-label />
        </div>
      </div>

      <div class="browse-toolbar-end">
        <n-badge
          dot
          :offset="[0, 5]"
          color="var(--accent-color-spotlight)"
          :show="browse.reducedView"
        >
          <n-button
            type="primary"
            :size="buttonSize"
            :title="$t('browse.toolbar.tipReducedView')"
            :focusable="false"
            :color="browse.reducedView ? theme.accentColors.lighter : undefined"
            :bordered="false"
            @click="browse.reducedView = !browse.reducedView"
          >
            <template #icon>
              <n-icon :component="browse.reducedView ? ExpandIcon : CompressIcon" />
            </template>
          </n-button>
        </n-badge>

        <n-badge :value="resourceDrawerBadgeLabel" color="var(--accent-color-spotlight)">
          <n-button
            type="primary"
            :size="buttonSize"
            :title="$t('browse.toolbar.tipOpenResourceList')"
            :focusable="false"
            :bordered="false"
            @click="browse.showResourceToggleDrawer = true"
          >
            <template #icon>
              <n-icon :component="ResourceIcon" />
            </template>
          </n-button>
        </n-badge>
      </div>
    </n-flex>
  </div>
</template>

<style scoped>
.browse-toolbar-container {
  position: sticky;
  top: -1px;

  width: 100%;
  max-width: var(--max-app-width);

  display: flex;
  flex-direction: column-reverse;
  gap: 0;

  border-radius: var(--border-radius);
  box-shadow: var(--block-box-shadow);
  transition: none;
}

.browse-toolbar-container > div:only-child {
  border-radius: var(--border-radius);
}

.browse-toolbar-container > div:last-child:not(:only-child) {
  border-top-left-radius: var(--border-radius);
  border-top-right-radius: var(--border-radius);
}

.browse-toolbar-container > div:first-child:not(:only-child) {
  border-bottom-left-radius: var(--border-radius);
  border-bottom-right-radius: var(--border-radius);
}

.browse-toolbar-container.affixed > div:last-child {
  border-top-left-radius: unset;
  border-top-right-radius: unset;
}

.browse-toolbar-container.affixed {
  max-width: unset;
  /* width: 100vw; */
  left: 0px;
  z-index: 1801;
  box-shadow: var(--fixed-box-shadow);
}

.browse-toolbar {
  padding: var(--gap-sm);
  box-shadow: var(--fixed-box-shadow);
}

.browse-toolbar-middle {
  flex-grow: 2;
  overflow: hidden;
  text-overflow: ellipsis;
  text-align: center;
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
  color: var(--base-color);
  font-weight: var(--font-weight-bold);
}

.browse-toolbar-container.affixed .browse-location-label {
  display: initial;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>

<style>
.browse-toolbar .n-badge > .n-badge-sup {
  color: #000;
}
</style>
