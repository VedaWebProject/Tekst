<script setup lang="ts">
import IconHeading from '@/components/generic/IconHeading.vue';
import { SearchResultsIcon } from '@/icons';
import { $t } from '@/i18n';
</script>

<template>
  <icon-heading level="1" :icon="SearchResultsIcon">
    {{ $t('search.results.heading') }}
  </icon-heading>

  <div class="content-block">FOO</div>
</template>
