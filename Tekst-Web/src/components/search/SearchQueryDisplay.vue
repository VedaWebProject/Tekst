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
  <div v-if="error" v-bind="$attrs" class="text-tiny">
    {{ $t('errors.unexpected') }}
  </div>
  <quick-search-query-display
    v-else-if="req?.type === 'quick'"
    v-bind="$attrs"
    :req="req"
    :total="total"
    :total-relation="totalRelation"
    :loading="loading"
  />
  <advanced-search-query-display
    v-else-if="req?.type === 'advanced'"
    v-bind="$attrs"
    :req="req"
    :total="total"
    :total-relation="totalRelation"
    :loading="loading"
  />
</template>
