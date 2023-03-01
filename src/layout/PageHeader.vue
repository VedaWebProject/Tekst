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
header {
  -webkit-box-shadow: 0px -14px 12px 12px rgba(0, 0, 0, 0.75);
  -moz-box-shadow: 0px -14px 12px 12px rgba(0, 0, 0, 0.75);
  box-shadow: 0px -14px 12px 12px rgba(0, 0, 0, 0.75);
}

#current-text-container {
  background-color: var(--accent-color);
  color: #fff;
}

#current-text {
  padding: var(--content-padding);
  max-width: var(--max-app-width);
  margin: 0 auto;
}
</style>
