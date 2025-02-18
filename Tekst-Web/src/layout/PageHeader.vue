<script setup lang="ts">
import TranslationDisplay from '@/components/generic/TranslationDisplay.vue';
import PrimaryNavBar from '@/components/navigation/PrimaryNavBar.vue';
import TextSelect from '@/components/navigation/TextSelect.vue';
import { useStateStore } from '@/stores';
import { NFlex } from 'naive-ui';

const state = useStateStore();
</script>

<template>
  <header>
    <primary-nav-bar />
    <div class="accent-color-bg" style="color: var(--base-color)">
      <n-flex size="large" justify="space-between" align="center" :wrap="false" class="page-header-bottom text-large">
        <text-select />
        <div
          v-if="!state.smallScreen && state.text?.subtitle?.length"
          class="current-text-subtitle ellipsis"
        >
          <translation-display :value="state.text?.subtitle" />
      </div>
      </n-flex>
    </div>
  </header>
</template>

<style scoped>
.page-header-bottom {
  height: 64px;
  padding: 0 var(--gap-lg);
  max-width: var(--max-app-width);
  margin: 0 auto;
}

.page-header-bottom > .current-text-subtitle {
  filter: opacity(0.6);
  white-space: nowrap;
}
</style>
