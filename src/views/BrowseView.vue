<script setup lang="ts">
import { usePlatformStore } from '@/stores/platform';
const pf = usePlatformStore();
</script>

<template>
  <h1>Browse {{ pf.get('general.title') }}</h1>
  <p>...</p>
</template>

<style scoped></style>
