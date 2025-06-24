<script setup lang="ts">
import BrowseLocationControls from '@/components/browse/BrowseLocationControls.vue';
import BrowseSearchResultsToolbar from '@/components/browse/BrowseSearchResultsToolbar.vue';
import LocationLabel from '@/components/LocationLabel.vue';
import TextColorIndicator from '@/components/TextColorIndicator.vue';
import { FocusViewOffIcon, FocusViewOnIcon, ResourceIcon } from '@/icons';
import { useBrowseStore, useSearchStore, useStateStore } from '@/stores';
import { NBadge, NButton, NFlex, NIcon } from 'naive-ui';
import { computed, nextTick, onMounted, ref } from 'vue';

const state = useStateStore();
const browse = useBrowseStore();
const search = useSearchStore();

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
      class="browse-toolbar primary-color-bg"
    >
      <browse-location-controls :button-size="buttonSize" />

      <div v-if="!state.smallScreen" class="browse-toolbar-middle browse-location-label text-small">
        <n-flex justify="center" align="center" :wrap="false">
          <text-color-indicator :title="state.text?.title" />
          <b style="text-align: center">{{ state.text?.title || '???' }}</b>
        </n-flex>
        <div><location-label /></div>
      </div>

      <div class="browse-toolbar-end">
        <n-badge dot :offset="[0, 5]" :show="browse.focusView">
          <n-button
            type="primary"
            :size="buttonSize"
            :title="$t('browse.toolbar.tipFocusView')"
            :focusable="false"
            :color="browse.focusView ? '#fff5' : undefined"
            :bordered="false"
            @click="browse.focusView = !browse.focusView"
          >
            <template #icon>
              <n-icon :component="browse.focusView ? FocusViewOnIcon : FocusViewOffIcon" />
            </template>
          </n-button>
        </n-badge>

        <n-badge
          :value="resourceDrawerBadgeLabel"
          color="var(--base-color)"
          class="active-resources-badge"
        >
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
  box-shadow: var(--affix-box-shadow);
}

.browse-toolbar {
  padding: var(--gap-sm) var(--gap-md);
}

.browse-toolbar-middle {
  flex: 2;
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
  visibility: hidden;
  color: var(--base-color);
}

.browse-toolbar-container.affixed .browse-location-label {
  visibility: initial;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.n-badge.active-resources-badge :deep(.n-badge-sup) {
  color: var(--text-color);
}
</style>
