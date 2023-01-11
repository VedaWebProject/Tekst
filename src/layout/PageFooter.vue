<script setup lang="ts">
import { useUiDataStore } from '@/stores/uiData';

const ui = useUiDataStore();
</script>

<template>
  <footer>
    Powered by
    <a :href="ui.get('platform.platform_website')" title="">
      {{ ui.get('platform.platform') }}
    </a>
    v{{ ui.get('platform.version') }} ({{ ui.get('platform.description') }}).
  </footer>
</template>

<style scoped>
footer {
  border: 1px dashed #ff9900;
  padding: 0.8em;
}
</style>
