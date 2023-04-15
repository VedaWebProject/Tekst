<script setup lang="ts">
import { usePlatformStore } from '@/stores';

const pf = usePlatformStore();
</script>

<template>
  <footer>
    <div id="footer-content">
      <div>{{ $t('server.welcomeTest') }}</div>
      <a :href="pf.data?.tekstInfo?.website" title="">
        {{ pf.data?.tekstInfo?.name }}
      </a>
      v{{ pf.data?.tekstInfo?.version }}
    </div>
  </footer>
</template>

<style scoped>
footer {
  /* border-top: 2px solid var(--accent-color); */
  padding: 1.75rem var(--layout-padding);
}

footer #footer-content {
  max-width: var(--max-app-width);
  margin: 0 auto;
}
</style>
