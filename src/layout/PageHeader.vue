<script setup lang="ts">
import BrowseToolbar from '@/components/BrowseToolbar.vue';
import NavBar from '@/components/NavBar.vue';
import TextSelect from '@/components/TextSelect.vue';
import { useStateStore } from '@/stores';

const state = useStateStore();
</script>

<template>
  <header>
    <NavBar />
    <div class="accent-color-bg">
      <div id="current-text">
        <TextSelect />
        <span class="current-text-subtitle">{{
          (!state.smallScreen && state.text?.subtitle) || '&nbsp;'
        }}</span>
      </div>
    </div>
  </header>
  <BrowseToolbar />
</template>

<style scoped>
#current-text {
  display: flex;
  column-gap: 24px;
  flex-wrap: wrap;
  justify-content: space-between;
  font-size: 1.2em;
  font-weight: 400;
  padding: 0.75rem var(--layout-padding);
  max-width: var(--max-app-width);
  margin: 0 auto;
}

#current-text .current-text-subtitle {
  font-weight: 300;
  filter: opacity(0.5);
}
</style>
