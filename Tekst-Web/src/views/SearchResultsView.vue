<script setup lang="ts">
import IconHeading from '@/components/generic/IconHeading.vue';
import { BookIcon, ErrorIcon, NothingFoundIcon, SearchResultsIcon } from '@/icons';
import SearchResult from '@/components/search/SearchResult.vue';
import { NIcon, NButton, NFlex, NList, NSpin, NPagination, NTime } from 'naive-ui';
import { usePlatformData } from '@/composables/platformData';
import { computed, onBeforeMount, ref } from 'vue';
import type { SearchResultProps } from '@/components/search/SearchResult.vue';
import { useResourcesStore, useSearchStore, useStateStore, useThemeStore } from '@/stores';
import HugeLabelledIcon from '@/components/generic/HugeLabelledIcon.vue';
import { $t } from '@/i18n';
import { createReusableTemplate, useMagicKeys, whenever } from '@vueuse/core';
import SearchResultsSortWidget from '@/components/search/SearchResultsSortWidget.vue';
import { isInputFocused, isOverlayOpen, pickTranslation, utcToLocalTime } from '@/utils';
import SearchQueryDisplay from '@/components/search/SearchQueryDisplay.vue';

const { pfData } = usePlatformData();
const state = useStateStore();
const resources = useResourcesStore();
const search = useSearchStore();
const theme = useThemeStore();
const [DefineTemplate, ReuseTemplate] = createReusableTemplate();
const { ArrowLeft, ArrowRight } = useMagicKeys();

const resultsContainer = ref<HTMLElement | null>(null);
const paginationSlots = computed(() => (state.smallScreen ? 4 : 9));

const results = computed<SearchResultProps[]>(() => {
  return (
    search.results?.hits.map((r) => {
      const text = pfData.value?.texts.find((t) => t.id === r.textId);
      return {
        id: r.id,
        label: r.label,
        fullLabel: r.fullLabel,
        textSlug: text?.slug || '',
        textTitle: text?.title || '',
        textColor: theme.getAccentColors(text?.id).base,
        level: r.level,
        levelLabel: state.getTextLevelLabel(r.textId, r.level) || '',
        position: r.position,
        scorePercent:
          search.results?.maxScore && r.score
            ? (r.score / search.results?.maxScore) * 100
            : undefined,
        highlight: r.highlight,
        smallScreen: state.smallScreen,
        resourceTitles: resources.resourceTitles,
      };
    }) || []
  );
});

const browseViewLabel = computed(
  () => pickTranslation(pfData.value?.state.navBrowseEntry, state.locale) || $t('nav.browse')
);

async function afterPaginate() {
  await search.searchSecondary();
  const resultsY = resultsContainer.value?.getBoundingClientRect().y || 0;
  if (resultsY < 0) {
    resultsContainer.value?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
}

// react to keyboard for in-/decreasing page number
whenever(ArrowRight, () => {
  if (!isOverlayOpen() && !isInputFocused()) {
    search.turnPage('next');
  }
});
whenever(ArrowLeft, () => {
  if (!isOverlayOpen() && !isInputFocused()) {
    search.turnPage('previous');
  }
});

onBeforeMount(() => {
  search.searchFromUrl();
});
</script>

<template>
  <define-template>
    <n-flex justify="end" class="pagination-container" align="center">
      <n-pagination
        v-if="search.results?.hits.length"
        v-model:page="search.settingsGeneral.pgn.pg"
        v-model:page-size="search.settingsGeneral.pgn.pgs"
        :simple="state.smallScreen"
        :page-sizes="[10, 25, 50]"
        :default-page-size="10"
        :page-slot="paginationSlots"
        :item-count="search.results.totalHits"
        :disabled="search.loading"
        show-size-picker
        size="medium"
        @update:page="() => afterPaginate()"
        @update:page-size="() => afterPaginate()"
      />
    </n-flex>
  </define-template>

  <icon-heading level="1" :icon="SearchResultsIcon">
    {{ $t('search.results.heading') }}
  </icon-heading>

  <n-flex justify="flex-end" align="center" style="gap: var(--gap-lg)" class="mb-lg">
    <search-query-display
      :req="search.currentRequest"
      :total="search.results?.totalHits"
      :total-relation="search.results?.totalHitsRelation"
      :took="search.results?.took"
      :error="search.error"
      style="flex-grow: 2"
    />
    <n-flex :wrap="false">
      <search-results-sort-widget
        v-model="search.settingsGeneral.sort"
        :disabled="!results.length || search.loading"
        @update:model-value="() => search.searchSecondary()"
      />
      <n-button
        type="primary"
        :title="$t('search.results.browse', { browse: browseViewLabel })"
        :focusable="false"
        :disabled="!results.length || search.loading"
        @click="() => search.browse(0)"
      >
        <template #icon>
          <n-icon :component="BookIcon" />
        </template>
        {{ browseViewLabel }}
      </n-button>
    </n-flex>
  </n-flex>

  <div ref="resultsContainer" class="content-block">
    <reuse-template />
    <n-spin
      v-if="search.loading"
      class="centered-spinner"
      :description="`${$t('search.results.searching')}...`"
    />
    <n-list v-else-if="results.length" clickable hoverable style="background-color: transparent">
      <search-result
        v-for="(result, index) in results"
        :key="result.id"
        v-bind="result"
        @click="search.browse(index)"
      />
    </n-list>
    <huge-labelled-icon
      v-else-if="search.error"
      :icon="ErrorIcon"
      :message="$t('errors.unexpected')"
    />
    <huge-labelled-icon v-else :icon="NothingFoundIcon" :message="$t('search.nothingFound')" />
    <reuse-template />
  </div>

  <div
    v-if="pfData?.state.indicesUpdatedAt"
    class="text-tiny translucent"
    style="text-align: center"
  >
    {{ $t('search.results.indexCreationTime') }}:
    <n-time :time="utcToLocalTime(pfData?.state.indicesUpdatedAt)" type="datetime" />
  </div>
</template>

<style scoped>
.pagination-container:first-child {
  margin-bottom: var(--gap-lg);
}

.pagination-container:last-child {
  margin-top: var(--gap-lg);
}
</style>
