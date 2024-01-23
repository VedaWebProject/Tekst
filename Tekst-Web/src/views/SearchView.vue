<script setup lang="ts">
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import IconHeading from '@/components/generic/IconHeading.vue';

import { AdvancedSearchIcon } from '@/icons';
</script>

<template>
  <IconHeading level="1" :icon="AdvancedSearchIcon">
    {{ $t('search.heading') }}
    <HelpButtonWidget help-key="searchView" />
  </IconHeading>
  <div class="content-block">
    <p>...</p>
  </div>
</template>

<style scoped></style>
