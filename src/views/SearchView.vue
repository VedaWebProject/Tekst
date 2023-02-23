<script setup lang="ts">
import { usePlatformStore } from '@/stores/platform';
const pf = usePlatformStore();
</script>

<template>
  <h1>Search {{ pf.get('info.platformName') }}</h1>
  <p>...</p>
</template>

<style scoped></style>
