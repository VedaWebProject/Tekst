<script setup lang="ts">
import { usePlatformStore } from '@/stores';

const pf = usePlatformStore();
</script>

<template>
  <footer>
    <div id="footer-content">
      <div>{{ $t('general.welcomeTest') }}</div>
      <a :href="pf.data?.textrigInfo?.website" title="">
        {{ pf.data?.textrigInfo?.name }}
      </a>
      v{{ pf.data?.textrigInfo?.version }}
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
