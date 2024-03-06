<script setup lang="ts">
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import { SearchIcon } from '@/icons';
</script>

<template>
  <icon-heading level="1" :icon="SearchIcon">
    {{ $t('search.heading') }}
    <help-button-widget help-key="searchView" />
  </icon-heading>
  <div class="content-block">...</div>
</template>

<style scoped></style>
