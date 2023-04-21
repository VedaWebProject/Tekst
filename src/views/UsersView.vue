<script setup lang="ts">
import { usePlatformStore } from '@/stores/platform';
const pf = usePlatformStore();
</script>

<template>
  <div class="content-block">
    <h1>{{ pf.data?.info?.platformName }} Admin Control Panel</h1>
    <p>...</p>
  </div>
</template>

<style scoped></style>
