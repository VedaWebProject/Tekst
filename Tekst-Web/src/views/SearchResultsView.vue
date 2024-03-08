<script setup lang="ts">
import IconHeading from '@/components/generic/IconHeading.vue';
import { NoContentIcon, SearchResultsIcon } from '@/icons';
import SearchResult from '@/components/search/SearchResult.vue';
import { NList, NTime } from 'naive-ui';
import { usePlatformData } from '@/composables/platformData';
import { computed, onBeforeMount, ref, watch } from 'vue';
import { POST, type AdvancedSearchQuery, type SearchResults } from '@/api';
import type { SearchResultProps } from '@/components/search/SearchResult.vue';
import { useStateStore } from '@/stores';
import HugeLabelledIcon from '@/components/generic/HugeLabelledIcon.vue';
import { useRoute } from 'vue-router';
import { Base64 } from 'js-base64';

const { pfData } = usePlatformData();
const state = useStateStore();
const route = useRoute();

const loading = ref(false);
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
        textColor: text?.accentColor || '#000',
        level: r.level,
        levelLabel: state.getTextLevelLabel(r.textId, r.level) || '',
        position: r.position,
        scorePercent: resultsData.value?.maxScore
          ? (r.score / resultsData.value?.maxScore) * 100
          : 0,
        highlight: r.highlight,
        smallScreen: state.smallScreen,
      };
    }) || []
);

async function runQuickSearch(query: string) {
  const { data, error } = await POST('/search/quick', {
    body: {
      query,
    },
  });
  if (!error) {
    resultsData.value = data;
  }
}

async function runAdvancedSearch(query: AdvancedSearchQuery) {
  const { data, error } = await POST('/search/advanced', {
    body: {
      query: query,
    },
  });
  if (!error) {
    resultsData.value = data;
  }
}

async function processQuery() {
  loading.value = true;
  const queryDecoded = Base64.decode(route.params.query?.toString() || '');
  let query;
  try {
    query = JSON.parse(queryDecoded);
    if (query && typeof query === 'object' && query.constructor === Object) {
      await runAdvancedSearch(query);
    }
  } finally {
    loading.value = false;
  }
}

watch(
  () => route.params.query,
  () => processQuery()
);

onBeforeMount(() => processQuery());
</script>

<template>
  <icon-heading level="1" :icon="SearchResultsIcon">
    {{ $t('search.results.heading') }}
  </icon-heading>

  <div
    v-if="resultsData"
    style="
      display: flex;
      justify-content: space-between;
      align-items: center;
      column-gap: var(--layout-gap);
      flex-wrap: wrap;
    "
    class="text-small translucent"
  >
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
  </div>

  <div class="content-block">
    <n-list v-if="results.length" clickable hoverable style="background-color: transparent">
      <search-result v-for="result in results" :key="result.id" v-bind="result" />
    </n-list>
    <huge-labelled-icon v-else :icon="NoContentIcon" :message="$t('search.nothingFound')" />
  </div>
</template>
