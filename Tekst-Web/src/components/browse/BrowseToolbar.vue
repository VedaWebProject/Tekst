<script setup lang="ts">
import BrowseLocationControls from '@/components/browse/BrowseLocationControls.vue';
import BrowseSearchResultsToolbar from '@/components/browse/BrowseSearchResultsToolbar.vue';
import LocationLabel from '@/components/LocationLabel.vue';
import { CompressIcon, ExpandIcon, ResourceIcon } from '@/icons';
import { useBrowseStore, useSearchStore, useStateStore, useThemeStore } from '@/stores';
import { NBadge, NButton, NFlex, NIcon } from 'naive-ui';
import { computed, nextTick, onMounted, ref } from 'vue';

const state = useStateStore();
const browse = useBrowseStore();
const search = useSearchStore();
const theme = useThemeStore();

const affixRef = ref();
const affixed = ref(false);

const toolbarTxtColor = computed(() => (theme.dark ? '#fff' : '#333'));

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
        ([e]) => {
          affixed.value = e.intersectionRatio < 1;
          e.target.classList.toggle('affixed', affixed.value);
        },
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
      class="browse-toolbar"
      :style="{ backgroundColor: theme.dark ? '#555' : '#d5d5d5' }"
    >
      <browse-location-controls
        :button-size="buttonSize"
        :color="toolbarTxtColor"
        data-tour-key="browseNav"
      />

      <div
        v-if="!state.smallScreen"
        class="browse-toolbar-middle browse-location-label"
        :style="{ color: toolbarTxtColor }"
        :title="affixed ? state.text?.title : undefined"
      >
        <n-flex justify="center" align="center" :wrap="false">
          <div
            class="text-color-indicator"
            :style="{ backgroundColor: theme.getTextColors().base }"
          ></div>
          <span v-if="!affixed">{{ state.text?.title || '???' }}</span>
          <span v-else><location-label /></span>
        </n-flex>
      </div>

      <div class="browse-toolbar-end">
        <n-badge dot :offset="[-2, 5]" :show="browse.focusView">
          <n-button
            quaternary
            :color="toolbarTxtColor"
            :style="{
              backgroundColor: browse.focusView ? 'var(--base-color-translucent)' : undefined,
            }"
            :size="buttonSize"
            :title="$t('browse.toolbar.tipFocusView')"
            :focusable="false"
            :bordered="false"
            data-tour-key="browseFocus"
            @click="browse.focusView = !browse.focusView"
          >
            <template #icon>
              <n-icon :component="browse.focusView ? ExpandIcon : CompressIcon" />
            </template>
          </n-button>
        </n-badge>

        <n-badge
          :value="resourceDrawerBadgeLabel"
          color="var(--base-color)"
          class="active-resources-badge"
        >
          <n-button
            quaternary
            :color="toolbarTxtColor"
            :size="buttonSize"
            :title="$t('browse.toolbar.tipOpenResourceList')"
            :focusable="false"
            :bordered="false"
            data-tour-key="browseResourceSelect"
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

.browse-toolbar .browse-location-label .text-color-indicator {
  width: 16px;
  height: 16px;
  border-radius: 50%;
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
