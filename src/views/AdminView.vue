<script setup lang="ts">
import { usePlatformStore } from '@/stores/platform';
const pf = usePlatformStore();
</script>

<template>
  <h1>{{ pf.get('info.platform_name') }} Admin Control Panel</h1>
  <p>...</p>
</template>

<style scoped></style>
