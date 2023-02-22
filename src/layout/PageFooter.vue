<script setup lang="ts">
import { usePlatformStore } from '@/stores';

const pf = usePlatformStore();
</script>

<template>
  <footer>
    Powered by
    <a :href="pf.get('general.platform_website')" title="">
      {{ pf.get('general.platform') }}
    </a>
    v{{ pf.get('general.version') }} ({{ pf.get('general.description') }}).
  </footer>
</template>

<style scoped>
footer {
  border-top: 3px solid var(--accent-color);
  padding: 0.8em;
}
</style>
