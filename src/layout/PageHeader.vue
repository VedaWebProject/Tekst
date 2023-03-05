<script setup lang="ts">
import NavBar from '@/components/NavBar.vue';
import TextSelect from '@/components/TextSelect.vue';
import { useStateStore } from '@/stores';

const state = useStateStore();
</script>

<template>
  <header>
    <NavBar />
    <div id="current-text-container">
      <div id="current-text">
        <TextSelect />
        <span class="current-text-subtitle">{{ state.text?.subtitle || '&nbsp;' }}</span>
      </div>
    </div>
  </header>
</template>

<style scoped>
#current-text-container {
  background-color: var(--accent-color);
  color: #fff;
}

#current-text {
  display: flex;
  column-gap: 24px;
  flex-wrap: wrap;
  justify-content: space-between;
  font-size: 1.1em;
  font-weight: 400;
  padding: 0.5rem var(--layout-padding);
  max-width: var(--max-app-width);
  margin: 0 auto;
}

#current-text .current-text-subtitle {
  font-weight: 300;
  filter: opacity(0.7);
}
</style>
