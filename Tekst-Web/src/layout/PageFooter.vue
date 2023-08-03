<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { usePlatformData } from '@/platformData';

const { pfData } = usePlatformData();
const { t } = useI18n({ useScope: 'global' });
</script>

<template>
  <footer>
    <div id="footer-content">
      <div>{{ t('server.welcomeTest') }}</div>
      <a :href="pfData?.tekstInfo?.website" title="">
        {{ pfData?.tekstInfo?.name }}
      </a>
      v{{ pfData?.tekstInfo?.version }}
    </div>
  </footer>
</template>

<style scoped>
footer {
  /* border-top: 2px solid var(--accent-color); */
  padding: 1.75rem var(--layout-gap);
}

footer #footer-content {
  max-width: var(--max-app-width);
  margin: 0 auto;
}
</style>
