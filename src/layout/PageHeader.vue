<script setup lang="ts">
import MainNavigation from '@/components/navigation/MainNavigation.vue';
import { usePlatformStore } from '@/stores';

const pf = usePlatformStore();
</script>

<template>
  <header>
    <img id="header-logo" :alt="`${pf.get('info.platformName')} Logo`" src="@/assets/logo.png" />
    <div id="page-title">{{ pf.get('info.platformName') }}</div>
    <MainNavigation id="main-navigation-bar" />
  </header>
</template>

<style scoped>
header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem;
}

header #header-logo {
  align-self: center;
  height: 56px;
  width: auto;
  margin-right: 1rem;
}

header #page-title {
  font-size: 1.2rem;
  margin-right: 1rem;
}

header #main-navigation-bar {
  flex-grow: 2;
}
</style>
