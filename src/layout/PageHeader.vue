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
        <div>Some selected text...</div>
      </div>
      <MainNavigation style="flex-grow: 2" />
    </div>
  </header>
</template>

<style scoped>
header {
  padding: 0.5rem;
  background-color: var(--accent-color);
}

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
  margin-right: 2rem;
}

header #header-title {
  font-size: 1.4rem;
}
</style>
