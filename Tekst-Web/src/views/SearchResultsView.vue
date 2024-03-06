<script setup lang="ts">
import IconHeading from '@/components/generic/IconHeading.vue';
import { SearchResultsIcon } from '@/icons';
import SearchResult from '@/components/search/SearchResult.vue';
import { NList } from 'naive-ui';
import { usePlatformData } from '@/composables/platformData';
import { computed, onBeforeMount, ref } from 'vue';
import { GET, type SearchResults } from '@/api';
import type { SearchResultProps } from '@/components/search/SearchResult.vue';
import { useStateStore } from '@/stores';
import { useRouter } from 'vue-router';

const { pfData } = usePlatformData();
const state = useStateStore();
const router = useRouter();

const resultsData = ref<SearchResults>();
const results = computed<SearchResultProps[]>(
  () =>
    resultsData.value?.hits.map((r) => {
      const text = pfData.value?.texts.find((t) => t.id === r.id);
      return {
        id: r.id,
        label: r.label,
        text: text?.title || '',
        textColor: text?.accentColor || '#000',
        level: r.level,
        levelLabel: state.textLevelLabels[r.level] || '',
        position: r.position,
        score: r.score,
      };
    }) || []
);

function handleResultClick(result: SearchResultProps) {
  router.push({
    name: 'browse',
    params: {
      text: pfData.value?.texts.find((t) => t.id === result.id)?.slug,
    },
    query: {
      lvl: result.level,
      pos: result.position,
    },
  });
}

onBeforeMount(async () => {
  const { data, error } = await GET('/search/quick', {
    params: {
      query: {
        q: '*',
      },
    },
  });
  if (!error) {
    resultsData.value = data;
  }
});
</script>

<template>
  <icon-heading level="1" :icon="SearchResultsIcon">
    {{ $t('search.results.heading') }}
  </icon-heading>

  <div class="content-block">
    <n-list clickable hoverable style="background-color: transparent">
      <search-result
        v-for="result in results"
        :key="result.id"
        v-bind="result"
        @click="handleResultClick"
      />
    </n-list>
  </div>
</template>
