<script setup lang="ts">
import IconHeading from '@/components/generic/IconHeading.vue';
import { SearchResultsIcon } from '@/icons';
</script>

<template>
  <icon-heading level="1" :icon="SearchResultsIcon">
    {{ $t('resources.heading') }}
  </icon-heading>
</template>
