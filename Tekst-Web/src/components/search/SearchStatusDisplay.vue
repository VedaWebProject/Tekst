<script setup lang="ts">
import { utcToLocalTime } from '@/utils';
import { NTime } from 'naive-ui';

defineProps<{
  totalHits: number;
  totalHitsRelation: 'eq' | 'gte';
  took: number;
  indicesUpdatedAt?: string | null;
  loading?: boolean;
  error?: boolean;
}>();
</script>

<template>
  <div class="text-tiny translucent">
    <span class="b">
      {{ totalHitsRelation === 'eq' ? '' : '≥' }}
      {{
        $t('search.results.count', {
          count: totalHits,
        })
      }}
    </span>
    <span>
      {{
        ' ' +
        $t('search.results.took', {
          ms: took,
        })
      }}
    </span>
    <span v-if="indicesUpdatedAt">
      {{ ' – ' + $t('search.results.indexCreationTime') }}:
      <n-time :time="utcToLocalTime(indicesUpdatedAt)" type="datetime" />
    </span>
    <span v-else-if="loading">
      {{ $t('search.results.searching') }}
    </span>
    <span v-else-if="error">
      {{ $t('errors.unexpected') }}
    </span>
  </div>
</template>
