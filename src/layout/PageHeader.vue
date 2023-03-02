<script setup lang="ts">
import NavBar from '@/components/NavBar.vue';
</script>

<template>
  <header>
    <NavBar />
    <div id="current-text-container">
      <div id="current-text">Some selected text...</div>
    </div>
  </header>
</template>

<style scoped>
#current-text-container {
  background-color: var(--accent-color);
  color: #fff;
}

#current-text {
  padding: var(--layout-padding);
  max-width: var(--max-app-width);
  margin: 0 auto;
}
</style>
