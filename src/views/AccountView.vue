<script setup lang="ts">
import { useUiDataStore } from '@/stores/uiData';
const ui = useUiDataStore();
</script>

<template>
  <h1>Your {{ ui.get('platform.title') }} Account</h1>
  <p>...</p>
</template>
