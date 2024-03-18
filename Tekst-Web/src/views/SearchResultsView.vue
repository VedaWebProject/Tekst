<script setup lang="ts">
import IconHeading from '@/components/generic/IconHeading.vue';
import { NothingFoundIcon, SearchResultsIcon } from '@/icons';
import SearchResult from '@/components/search/SearchResult.vue';
import { NSpace, NList, NTime, NSpin, NPagination } from 'naive-ui';
import { usePlatformData } from '@/composables/platformData';
import { computed, onBeforeMount, ref, watch } from 'vue';
import { POST, type SearchRequestBody, type SearchResults, type SortingPreset } from '@/api';
import type { SearchResultProps } from '@/components/search/SearchResult.vue';
import { useSearchStore, useStateStore, useThemeStore } from '@/stores';
import HugeLabelledIcon from '@/components/generic/HugeLabelledIcon.vue';
import { useRoute, useRouter } from 'vue-router';
import { useMessages } from '@/composables/messages';
import { $t } from '@/i18n';
import { createReusableTemplate } from '@vueuse/core';
import SearchResultsSortWidget from '@/components/search/SearchResultsSortWidget.vue';

const { pfData } = usePlatformData();
const state = useStateStore();
const search = useSearchStore();
const route = useRoute();
const router = useRouter();
const theme = useThemeStore();
const { message } = useMessages();
const [DefineTemplate, ReuseTemplate] = createReusableTemplate();

const searchReq = ref<SearchRequestBody>();
const paginationDefaults = () => ({
  page: 1,
  pageSize: 10,
});
const pagination = ref(paginationDefaults());
const paginationSlots = computed(() => (state.smallScreen ? 4 : 9));
const paginationSize = computed(() => (state.smallScreen ? undefined : 'large'));
const paginationExtrasSize = computed(() => (state.smallScreen ? 'small' : undefined));
const sortingPreset = ref<SortingPreset>();

const loading = ref(false);
const searchError = ref(false);
const resultsData = ref<SearchResults>();
const results = computed<SearchResultProps[]>(
  () =>
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
      };
    }) || []
);

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
        pg: pagination.value.page,
        pgs: pagination.value.pageSize,
        sort: sortingPreset.value,
      },
    },
  });
  if (!error) {
    resultsData.value = data;
  } else {
    searchError.value = true;
  }
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

onBeforeMount(() => processQuery());
</script>

<template>
  <define-template>
    <n-space justify="end" class="pagination-container" align="center">
      <n-pagination
        v-if="resultsData?.hits.length"
        v-model:page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 25, 50]"
        :default-page-size="10"
        :page-slot="paginationSlots"
        :item-count="resultsData.totalHits"
        :disabled="loading"
        :size="paginationSize"
        show-size-picker
        @update:page="() => execSearch()"
        @update:page-size="() => execSearch(true)"
      >
        <template #suffix>
          <search-results-sort-widget
            v-model:value="sortingPreset"
            :size="paginationExtrasSize"
            :disabled="loading"
            @update:value="handleSortingChange"
          />
        </template>
      </n-pagination>
    </n-space>
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
        {{
          $t('search.results.results', {
            count: (resultsData.totalHitsRelation === 'eq' ? '' : '≥') + resultsData.totalHits,
            ms: resultsData.took,
          })
        }}
      </div>
      <div>
        {{ $t('search.results.indexCreationTime') }}:
        <n-time :time="new Date(resultsData.indexCreationTime)" type="datetime" />
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
