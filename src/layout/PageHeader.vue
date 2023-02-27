<script setup lang="ts">
import MainNavigation from '@/components/navigation/MainNavigation.vue';
import { usePlatformStore } from '@/stores';

const pf = usePlatformStore();
</script>

<template>
  <header>
    <div id="header-container">
      <img id="header-logo" :alt="`${pf.get('info.platformName')} Logo`" src="@/assets/logo.png" />
      <div id="header-title-container">
        <div id="header-title">{{ pf.get('info.platformName') }}</div>
      </div>
      <MainNavigation style="flex-grow: 2" />
    </div>
    <div id="current-text">Some selected text...</div>
  </header>
</template>

<style scoped>
header #header-container {
  display: flex;
  align-items: center;
  justify-content: start;
  /* flex-wrap: wrap; */
}

header #header-logo {
  align-self: center;
  height: 48px;
  width: auto;
  margin-right: 1rem;
}

header #header-title-container {
  margin-right: 3rem;
}

header #header-title {
  font-size: 1.4rem;
}

header #current-text {
  background-color: var(--accent-color);
  color: var(--theme-text-color-inverted);
}

header #header-container,
header #current-text {
  padding: 0.75rem;
}
</style>
