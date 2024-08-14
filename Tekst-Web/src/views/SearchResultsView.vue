<script setup lang="ts">
import IconHeading from '@/components/generic/IconHeading.vue';
import { ErrorIcon, NothingFoundIcon, SearchResultsIcon } from '@/icons';
import SearchResult from '@/components/search/SearchResult.vue';
import { NFlex, NList, NTime, NSpin, NPagination } from 'naive-ui';
import { usePlatformData } from '@/composables/platformData';
import { computed, onBeforeMount, ref, watch } from 'vue';
import { POST, type SearchRequestBody, type SearchResults, type SortingPreset } from '@/api';
import type { SearchResultProps } from '@/components/search/SearchResult.vue';
import { useResourcesStore, useSearchStore, useStateStore, useThemeStore } from '@/stores';
import HugeLabelledIcon from '@/components/generic/HugeLabelledIcon.vue';
import { useRoute, useRouter } from 'vue-router';
import { useMessages } from '@/composables/messages';
import { $t } from '@/i18n';
import { createReusableTemplate, useMagicKeys, whenever } from '@vueuse/core';
import SearchResultsSortWidget from '@/components/search/SearchResultsSortWidget.vue';
import { isOverlayOpen, pickTranslation, utcToLocalTime } from '@/utils';

const { pfData } = usePlatformData();
const state = useStateStore();
const resources = useResourcesStore();
const search = useSearchStore();
const route = useRoute();
const router = useRouter();
const theme = useThemeStore();
const { message } = useMessages();
const [DefineTemplate, ReuseTemplate] = createReusableTemplate();
const { ArrowLeft, ArrowRight } = useMagicKeys();

const searchReq = ref<SearchRequestBody>();
const paginationDefaults = () => ({
  page: 1,
  pageSize: 10,
});
const pagination = ref(paginationDefaults());
const paginationSlots = computed(() => (state.smallScreen ? 4 : 9));
const sortingPreset = ref<SortingPreset>();

const loading = ref(false);
const searchError = ref(false);
const resultsData = ref<SearchResults>();
const results = computed<SearchResultProps[]>(() => {
  const resourceTitles = Object.fromEntries(
    resources.all.map((r) => [r.id, pickTranslation(r.title, state.locale)])
  );
  return (
    resultsData.value?.hits.map((r) => {
      const text = pfData.value?.texts.find((t) => t.id === r.textId);
      return {
        id: r.id,
        label: r.label,
        fullLabel: r.fullLabel,
        textSlug: text?.slug || '',
        textTitle: text?.title || '',
        textColor: theme.generateAccentColorVariants(text?.accentColor).base,
        level: r.level,
        levelLabel: state.getTextLevelLabel(r.textId, r.level) || '',
        position: r.position,
        scorePercent:
          resultsData.value?.maxScore && r.score
            ? (r.score / resultsData.value?.maxScore) * 100
            : undefined,
        highlight: r.highlight,
        smallScreen: state.smallScreen,
        resourceTitles,
      };
    }) || []
  );
});

async function execSearch(resetPage?: boolean) {
  if (!searchReq.value) return;
  if (resetPage) {
    pagination.value.page = paginationDefaults().page;
  }
  loading.value = true;
  searchError.value = false;
  const { data, error } = await POST('/search', {
    body: {
      ...searchReq.value,
      gen: {
        ...searchReq.value?.gen,
        pgn: {
          pg: pagination.value.page,
          pgs: pagination.value.pageSize,
        },
        sort: sortingPreset.value,
      },
    },
  });
  if (!error) {
    resultsData.value = data;
  } else {
    searchError.value = true;
  }
  window.scrollTo(0, 0);
  loading.value = false;
}

async function processQuery() {
  loading.value = true;
  searchError.value = false;
  resultsData.value = undefined;
  pagination.value.page = 1;
  try {
    searchReq.value = search.decodeQueryParam();
    if (!searchReq.value || !['quick', 'advanced'].includes(searchReq.value.type)) {
      throw new Error();
    }
    search.lastReq = searchReq.value;
    sortingPreset.value = searchReq.value.gen?.sort || undefined;
    await execSearch();
  } catch {
    message.error($t('search.results.msgInvalidRequest'));
  } finally {
    loading.value = false;
  }
}

function handleSortingChange() {
  router.replace({
    name: 'searchResults',
    query: {
      q: search.encodeQueryParam({
        ...searchReq.value,
        gen: {
          ...searchReq.value?.gen,
          sort: sortingPreset.value,
        },
      } as SearchRequestBody),
    },
  });
}

watch(
  () => route.query.q,
  () => processQuery()
);

function turnPage(direction: 'previous' | 'next') {
  if (!resultsData.value) return;
  const currPage = pagination.value.page;
  pagination.value.page =
    direction === 'previous'
      ? Math.max(1, pagination.value.page - 1)
      : Math.min(
          pagination.value.page + 1,
          Math.floor(resultsData.value.totalHits / pagination.value.pageSize) + 1
        );
  currPage !== pagination.value.page && execSearch();
}

// react to keyboard for in-/decreasing page number
whenever(ArrowRight, () => {
  !isOverlayOpen() && turnPage('next');
});
whenever(ArrowLeft, () => {
  !isOverlayOpen() && turnPage('previous');
});

onBeforeMount(() => processQuery());
</script>

<template>
  <define-template>
    <n-flex justify="end" class="pagination-container" align="center">
      <n-pagination
        v-if="resultsData?.hits.length"
        v-model:page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :simple="state.smallScreen"
        :page-sizes="[10, 25, 50]"
        :default-page-size="10"
        :page-slot="paginationSlots"
        :item-count="resultsData.totalHits"
        :disabled="loading"
        show-size-picker
        size="medium"
        @update:page="() => execSearch()"
        @update:page-size="() => execSearch(true)"
      >
        <template #suffix>
          <search-results-sort-widget
            v-model="sortingPreset"
            size="small"
            :disabled="loading"
            @update:model-value="handleSortingChange"
          />
        </template>
      </n-pagination>
    </n-flex>
  </define-template>

  <icon-heading level="1" :icon="SearchResultsIcon">
    {{ $t('search.results.heading') }}
  </icon-heading>

  <div
    style="
      display: flex;
      justify-content: space-between;
      align-items: center;
      column-gap: var(--layout-gap);
      flex-wrap: wrap;
    "
    class="text-small translucent"
  >
    <template v-if="resultsData">
      <div>
        {{ resultsData.totalHitsRelation === 'eq' ? '' : '≥' }}
        {{
          $t('search.results.count', {
            count: resultsData.totalHits,
          })
        }}
        {{
          $t('search.results.took', {
            ms: resultsData.took,
          })
        }}
      </div>
      <div v-if="pfData?.state.indicesCreatedAt">
        {{ $t('search.results.indexCreationTime') }}:
        <n-time :time="utcToLocalTime(pfData.state.indicesCreatedAt)" type="datetime" />
      </div>
    </template>
    <template v-else-if="loading">
      {{ $t('search.results.searching') }}
    </template>
    <template v-else-if="searchError">
      {{ $t('errors.unexpected') }}
    </template>
  </div>

  <div class="content-block">
    <reuse-template />
    <n-spin v-if="loading" class="centered-spinner" :description="$t('search.results.searching')" />
    <n-list v-else-if="results.length" clickable hoverable style="background-color: transparent">
      <search-result v-for="result in results" :key="result.id" v-bind="result" />
    </n-list>
    <huge-labelled-icon
      v-else-if="searchError"
      :icon="ErrorIcon"
      :message="$t('errors.unexpected')"
    />
    <huge-labelled-icon v-else :icon="NothingFoundIcon" :message="$t('search.nothingFound')" />
    <reuse-template />
  </div>
</template>

<style scoped>
.pagination-container:first-child {
  margin-bottom: var(--layout-gap);
}
.pagination-container:last-child {
  margin-top: var(--layout-gap);
}
</style>
