<script setup lang="ts">
import type { AdvancedSearchRequestBody, QuickSearchRequestBody } from '@/api';
import AdvancedSearchQueryDisplay from '@/components/search/AdvancedSearchQueryDisplay.vue';
import QuickSearchQueryDisplay from '@/components/search/QuickSearchQueryDisplay.vue';

withDefaults(
  defineProps<{
    req?: QuickSearchRequestBody | AdvancedSearchRequestBody;
    total?: number;
    totalRelation?: 'eq' | 'gte';
    loading?: boolean;
    error?: boolean;
  }>(),
  {
    req: undefined,
    total: undefined,
    totalRelation: undefined,
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
    :loading="loading"
  />
  <advanced-search-query-display
    v-else-if="req?.type === 'advanced'"
    :req="req"
    :total="total"
    :total-relation="totalRelation"
    :loading="loading"
  />
</template>
