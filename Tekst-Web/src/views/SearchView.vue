<script setup lang="ts">
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import { SearchIcon } from '@/icons';

function generateScoreColor(scorePercent: number) {
  return `rgba(${180 - scorePercent * 1.8}, ${scorePercent * 1.8}, 0, 0.2)`;
}
</script>

<template>
  <icon-heading level="1" :icon="SearchIcon">
    {{ $t('search.heading') }}
    <help-button-widget help-key="searchView" />
  </icon-heading>
  <div class="content-block">
    <div style="height: 32px" :style="{ backgroundColor: generateScoreColor(100) }">
      Relevance: 100%
    </div>
    <div style="height: 32px" :style="{ backgroundColor: generateScoreColor(90) }">100%</div>
    <div style="height: 32px" :style="{ backgroundColor: generateScoreColor(80) }">100%</div>
    <div style="height: 32px" :style="{ backgroundColor: generateScoreColor(70) }">100%</div>
    <div style="height: 32px" :style="{ backgroundColor: generateScoreColor(60) }">100%</div>
    <div style="height: 32px" :style="{ backgroundColor: generateScoreColor(50) }">100%</div>
    <div style="height: 32px" :style="{ backgroundColor: generateScoreColor(40) }">100%</div>
    <div style="height: 32px" :style="{ backgroundColor: generateScoreColor(30) }">100%</div>
    <div style="height: 32px" :style="{ backgroundColor: generateScoreColor(20) }">100%</div>
    <div style="height: 32px" :style="{ backgroundColor: generateScoreColor(10) }">100%</div>
    <div style="height: 32px" :style="{ backgroundColor: generateScoreColor(1) }">100%</div>
  </div>
</template>

<style scoped></style>
