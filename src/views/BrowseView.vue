<script setup lang="ts">
import { usePlatformStore } from '@/stores/platform';
const pf = usePlatformStore();
</script>

<template>
  <h1>Browse {{ pf.get('info.platform_name') }}</h1>
  <p>...</p>
</template>

<style scoped></style>
