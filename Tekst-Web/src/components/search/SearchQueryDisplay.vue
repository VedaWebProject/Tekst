<script setup lang="ts">
import type { SearchRequestBody } from '@/api';
import QuickSearchQueryDisplay from '@/components/search/QuickSearchQueryDisplay.vue';
import AdvancedSearchQueryDisplay from '@/components/search/AdvancedSearchQueryDisplay.vue';

withDefaults(
  defineProps<{
    req?: SearchRequestBody;
    total?: number;
    totalRelation?: 'eq' | 'gte';
    took?: number;
    error?: boolean;
  }>(),
  {
    req: undefined,
    total: undefined,
    totalRelation: undefined,
    took: undefined,
  }
);
</script>

<template>
  <div v-if="error" class="text-tiny">
    {{ $t('errors.unexpected') }}
  </div>
  <quick-search-query-display
    v-else-if="req?.type === 'quick'"
    :req="req"
    :total="total"
    :total-relation="totalRelation"
    :took="took"
  />
  <advanced-search-query-display
    v-else-if="req?.type === 'advanced'"
    :req="req"
    :total="total"
    :total-relation="totalRelation"
    :took="took"
  />
</template>
