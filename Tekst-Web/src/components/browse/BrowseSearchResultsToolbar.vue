<script setup lang="ts">
import { NFlex, NButton, NIcon } from 'naive-ui';
import {
  SearchResultsIcon,
  ClearIcon,
  SkipPreviousIcon,
  SkipNextIcon,
  SearchIcon,
  RefreshIcon,
} from '@/icons';
import { useBrowseStore, useSearchStore } from '@/stores';
import { computed } from 'vue';

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

function gotoSearchResults() {
  search.gotoSearchResultsView();
}

function stopBrowsing() {
  search.browseHits = false;
  search.browseHitIndexOnPage = 0;
}
</script>

<template>
  <div v-if="search.browseHits" class="bsr-container mt-sm">
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
          @click="() => search.browseSkipTo('previous')"
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
          @click="() => search.browseSkipTo('next')"
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
          {{ $t('general.loading') }}
        </n-flex>
      </n-flex>

      <n-flex :wrap="false">
        <!-- just a spacer button to match the alignment of the browse toolbar -->
        <n-button
          quaternary
          :size="buttonSize"
          :focusable="false"
          :bordered="false"
          style="visibility: hidden"
        >
          <template #icon>
            <n-icon :component="SearchIcon" />
          </template>
        </n-button>
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
  border-radius: var(--border-radius);
  box-shadow: var(--fixed-box-shadow);
  background-color: var(--base-color);
}

.bsr-toolbar {
  padding: var(--gap-sm);
  border-radius: var(--border-radius);
  background-color: var(--accent-color-fade3);
}

.bsr-toolbar-middle {
  flex-grow: 2;
}
</style>
