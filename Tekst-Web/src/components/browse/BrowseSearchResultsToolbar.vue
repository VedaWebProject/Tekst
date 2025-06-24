<script setup lang="ts">
import {
  CheckListIcon,
  ClearIcon,
  RefreshIcon,
  SearchIcon,
  SearchResultsIcon,
  SkipNextIcon,
  SkipPreviousIcon,
} from '@/icons';
import { useBrowseStore, useSearchStore } from '@/stores';
import { NBadge, NButton, NFlex, NIcon } from 'naive-ui';
import { computed, onMounted } from 'vue';

withDefaults(
  defineProps<{
    smallScreen?: boolean;
    buttonSize?: 'small' | 'large';
  }>(),
  {
    buttonSize: 'large',
  }
);

const browse = useBrowseStore();
const search = useSearchStore();

const resultNo = computed(
  () =>
    search.settingsGeneral.pgn.pgs * (search.settingsGeneral.pgn.pg - 1) +
    search.browseHitIndexOnPage +
    1
);

const viewingSearchResult = computed(
  () => search.browseCurrHit?.id === browse.locationPathHead?.id
);

async function skip(direction: 'previous' | 'next') {
  await search.browseSkipTo(direction);
  if (search.browseHitResourcesActive) {
    browse.setResourcesActiveState(search.browseHitResources, true, true);
  }
}

function gotoSearchResults() {
  search.gotoSearchResultsView();
}

function switchBrowseHitResourcesActive(active: boolean) {
  search.browseHitResourcesActive = active;
  if (active) {
    browse.setResourcesActiveState(search.browseHitResources, true, true);
  } else {
    browse.setResourcesActiveState();
  }
}

function stopBrowsing() {
  search.stopBrowsing();
  browse.setResourcesActiveState();
}

onMounted(() => {
  if (search.browseHits && search.browseHitResourcesActive) {
    browse.setResourcesActiveState(search.browseHitResources, true, true);
  }
});
</script>

<template>
  <div v-if="search.browseHits" class="bsr-container">
    <n-flex justify="space-between" align="center" :wrap="false" class="bsr-toolbar">
      <n-flex :wrap="false">
        <!-- skip to previous search result -->
        <n-button
          quaternary
          :size="buttonSize"
          :title="$t('search.results.browsePrev')"
          :focusable="false"
          :disabled="search.loading || resultNo === 1"
          :bordered="false"
          @click="() => skip('previous')"
        >
          <template #icon>
            <n-icon :component="SkipPreviousIcon" />
          </template>
        </n-button>
        <!-- go to search results -->
        <n-button
          quaternary
          :size="buttonSize"
          :title="$t('search.results.heading')"
          :focusable="false"
          :disabled="search.loading"
          :bordered="false"
          @click="gotoSearchResults"
        >
          <template #icon>
            <n-icon :component="SearchResultsIcon" />
          </template>
        </n-button>
        <!-- skip to next search result -->
        <n-button
          quaternary
          :size="buttonSize"
          :title="$t('search.results.browseNext')"
          :focusable="false"
          :disabled="search.loading || resultNo === search.results?.totalHits"
          :bordered="false"
          @click="() => skip('next')"
        >
          <template #icon>
            <n-icon :component="SkipNextIcon" />
          </template>
        </n-button>
      </n-flex>

      <!-- show the current result number in the middle -->
      <n-flex
        v-if="!smallScreen"
        justify="center"
        align="center"
        :wrap="false"
        class="bsr-toolbar-middle text-small"
      >
        <n-flex
          v-if="!search.loading"
          align="center"
          :wrap="false"
          :style="{
            opacity: viewingSearchResult ? '1' : '0',
            transition: 'opacity 0.2s ease-in-out',
          }"
        >
          <n-icon :component="SearchIcon" />
          {{
            $t('search.results.browseCurrHit', {
              no: resultNo,
              of: search.results?.totalHits || '?',
            })
          }}
        </n-flex>
        <n-flex v-else align="center" :wrap="false" class="translucent">
          <n-icon :component="RefreshIcon" />
          {{ $t('common.loading') }}
        </n-flex>
      </n-flex>

      <n-flex :wrap="false">
        <!-- keep active resources in sync with relevant resources from current hit? -->
        <n-badge dot :offset="[0, 5]" :show="search.browseHitResourcesActive">
          <n-button
            :quaternary="!search.browseHitResourcesActive"
            :tertiary="search.browseHitResourcesActive"
            :size="buttonSize"
            :title="$t('search.results.browseHitResourcesActive')"
            :focusable="false"
            :bordered="false"
            @click="() => switchBrowseHitResourcesActive(!search.browseHitResourcesActive)"
          >
            <template #icon>
              <n-icon :component="CheckListIcon" />
            </template>
          </n-button>
        </n-badge>
        <!-- stop browsing search results -->
        <n-button
          quaternary
          :size="buttonSize"
          :title="$t('search.results.browseStop')"
          :focusable="false"
          :bordered="false"
          @click="stopBrowsing"
        >
          <template #icon>
            <n-icon :component="ClearIcon" />
          </template>
        </n-button>
      </n-flex>
    </n-flex>
  </div>
</template>

<style scoped>
.bsr-container {
  background-color: var(--base-color);
}

.bsr-toolbar {
  padding: var(--gap-sm);
  background-color: var(--primary-color-fade3);
  border-bottom-left-radius: var(--border-radius);
  border-bottom-right-radius: var(--border-radius);
}

.bsr-toolbar-middle {
  flex: 2;
}

:deep(.n-badge > .n-badge-sup) {
  color: #000;
}
</style>
