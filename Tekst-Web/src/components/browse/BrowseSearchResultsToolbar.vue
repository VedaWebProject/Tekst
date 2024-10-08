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
  <div v-if="search.browseHits" class="bsr-container accent-color-bg mt-sm box-shadow">
    <n-flex justify="space-between" align="center" :wrap="false">
      <n-flex :wrap="false">
        <!-- skip to previous search result -->
        <n-button
          type="primary"
          :size="buttonSize"
          :title="$t('search.results.browsePrev')"
          :focusable="false"
          :disabled="search.loading || resultNo === 1"
          @click="() => search.browseSkipTo('previous')"
        >
          <template #icon>
            <n-icon :component="SkipPreviousIcon" />
          </template>
        </n-button>
        <!-- go to search results -->
        <n-button
          type="primary"
          :size="buttonSize"
          :title="$t('search.results.heading')"
          :focusable="false"
          :disabled="search.loading"
          @click="gotoSearchResults"
        >
          <template #icon>
            <n-icon :component="SearchResultsIcon" />
          </template>
        </n-button>
        <!-- skip to next search result -->
        <n-button
          type="primary"
          :size="buttonSize"
          :title="$t('search.results.browseNext')"
          :focusable="false"
          :disabled="search.loading || resultNo === search.results?.totalHits"
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
        <n-icon :component="!search.loading ? SearchIcon : RefreshIcon" />
        <div v-if="!search.loading && viewingSearchResult">
          {{
            $t('search.results.browseCurrHit', {
              no: resultNo,
              of: search.results?.totalHits || '?',
            })
          }}
        </div>
        <div v-else-if="!search.loading && !viewingSearchResult">–</div>
        <div v-else class="translucent">
          {{ $t('general.loading') }}
        </div>
      </n-flex>

      <n-flex :wrap="false">
        <!-- just a spacer button to match the alignment of the browse toolbar -->
        <n-button type="primary" :size="buttonSize" :focusable="false" style="visibility: hidden">
          <template #icon>
            <n-icon :component="SearchIcon" />
          </template>
        </n-button>
        <!-- stop browsing search results -->
        <n-button
          type="primary"
          :size="buttonSize"
          :title="$t('search.results.browseStop')"
          :focusable="false"
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
  padding: var(--gap-sm);
}

.bsr-toolbar-middle {
  flex-grow: 2;
  color: var(--base-color);
}
</style>
