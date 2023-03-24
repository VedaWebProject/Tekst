<script setup lang="ts">
import BrowseLocationLabel from '@/components/browse/BrowseLocationLabel.vue';
import BrowseToolbar from '@/components/browse/BrowseToolbar.vue';
import { useStateStore } from '@/stores';

// const browse = useBrowseStore();
const state = useStateStore();
</script>

<template>
  <div class="browse-heading-container">
    <h1>{{ state.text?.title }}</h1>
    <h2><BrowseLocationLabel /></h2>
  </div>

  <BrowseToolbar />

  <div class="content-block">
    <p>...</p>
    <p>...</p>
    <p>...</p>
    <p>...</p>
    <p>...</p>
    <p>...</p>
    <p>...</p>
    <p>...</p>
    <p>...</p>
    <p>...</p>
    <p>...</p>
    <p>...</p>
    <p>...</p>
    <p>...</p>
    <p>...</p>
  </div>
</template>

<style scoped>
.browse-heading-container {
  display: flex;
  flex-wrap: wrap;
  column-gap: 24px;
  row-gap: 12px;
  align-items: baseline;
  margin: 10px 0 24px 0;
}

.browse-heading-container > h1 {
  margin: 0;
}

.browse-heading-container > h2 {
  flex-grow: 2;
  overflow: hidden;
  text-overflow: ellipsis;
  opacity: 0.75;
  margin: 0;
  white-space: nowrap;
}
</style>
