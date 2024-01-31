<script setup lang="ts">
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import IconHeading from '@/components/generic/IconHeading.vue';

import { AdvancedSearchIcon } from '@/icons';
</script>

<template>
  <icon-heading level="1" :icon="AdvancedSearchIcon">
    {{ $t('search.heading') }}
    <help-button-widget help-key="searchView" />
  </icon-heading>
  <div class="content-block">
    <p>...</p>
  </div>
</template>

<style scoped></style>
