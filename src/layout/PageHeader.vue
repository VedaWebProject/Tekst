<script setup lang="ts">
import BrowseToolbar from '@/components/browse/BrowseToolbar.vue';
import NavBar from '@/components/navigation/NavBar.vue';
import TextSelect from '@/components/widgets/TextSelect.vue';
import { useStateStore } from '@/stores';

const state = useStateStore();
</script>

<template>
  <header>
    <NavBar />
    <div class="accent-color-bg">
      <div id="current-text">
        <TextSelect />
        <span v-if="!state.smallScreen" class="current-text-subtitle">
          {{ state.text?.subtitle }}
        </span>
      </div>
    </div>
  </header>
  <BrowseToolbar />
</template>

<style scoped>
#current-text {
  --current-text-height: 64px;
  height: var(--current-text-height);
  display: flex;
  column-gap: 24px;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  padding: 0 var(--layout-padding);
  max-width: var(--max-app-width);
  margin: 0 auto;
}

#current-text .current-text-subtitle {
  font-weight: 300;
  filter: opacity(0.5);
}
</style>
