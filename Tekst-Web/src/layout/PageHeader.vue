<script setup lang="ts">
import PrimaryNavBar from '@/components/navigation/PrimaryNavBar.vue';
import TextSelect from '@/components/navigation/TextSelect.vue';
import QuickSearch from '@/components/search/QuickSearch.vue';
import { NFlex } from 'naive-ui';
</script>

<template>
  <header>
    <primary-nav-bar />
    <div class="accent-color-bg" style="color: var(--base-color)">
      <n-flex
        :size="[32, 12]"
        justify="space-between"
        align="center"
        class="page-header-bottom text-large"
      >
        <text-select style="flex: 6 1" />
        <quick-search style="flex: 1 1 300px" />
      </n-flex>
    </div>
  </header>
</template>

<style scoped>
.page-header-bottom {
  padding: var(--gap-md) var(--gap-lg);
  max-width: var(--max-app-width);
  margin: 0 auto;
}

.page-header-bottom > * {
  max-width: 100%;
}
</style>
