<script setup lang="ts">
import { useUiDataStore } from '@/stores/uiData';

const ui = useUiDataStore();
</script>

<template>
  <footer>
    Powered by
    <a :href="ui.data.platform.platform_website" title="">
      {{ ui.data.platform.platform }}
    </a>
    v{{ ui.data.platform.version }} ({{ ui.data.platform.description }}).
  </footer>
</template>

<style scoped>
footer {
  border: 1px dashed #ff9900;
  padding: 0.8em;
}
</style>
