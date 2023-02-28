<script setup lang="ts">
import { usePlatformStore } from '@/stores';

const pf = usePlatformStore();
</script>

<template>
  <footer>
    <div id="footer-content">
      <div>{{ $t('general.welcomeTest') }}</div>
      Powered by
      <a :href="pf.get('textrigInfo.website')" title="">
        {{ pf.get('textrigInfo.name') }}
      </a>
      v{{ pf.get('textrigInfo.version') }} ({{ pf.get('textrigInfo.description') }}).
    </div>
  </footer>
</template>

<style scoped>
footer {
  border-top: 4px solid var(--accent-color);
  padding: var(--content-padding);
}

footer #footer-content {
  max-width: var(--max-app-width);
  margin: 0 auto;
}
</style>
