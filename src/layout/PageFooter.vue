<script setup lang="ts">
import { usePlatformStore } from '@/stores';

const pf = usePlatformStore();
</script>

<template>
  <footer>
    <div>{{ $t('general.welcomeTest') }}</div>
    Powered by
    <a :href="pf.get('textrigInfo.website')" title="">
      {{ pf.get('textrigInfo.name') }}
    </a>
    v{{ pf.get('textrigInfo.version') }} ({{ pf.get('textrigInfo.description') }}).
  </footer>
</template>

<style scoped>
footer {
  border-top: 3px solid var(--accent-color);
  padding: 0.8em;
}
</style>
