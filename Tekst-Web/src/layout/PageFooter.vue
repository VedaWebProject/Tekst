<script setup lang="ts">
import SegmentRenderer from '@/components/SegmentRenderer.vue';
import { usePlatformData } from '@/platformData';
import { computed } from 'vue';

const { pfData } = usePlatformData();
const siteNotice = computed(
  () => !!pfData.value?.systemSegments.find((s) => s.key === 'systemSiteNotice')
);
const privacyPolicy = computed(
  () => !!pfData.value?.systemSegments.find((s) => s.key === 'systemPrivacyPolicy')
);
</script>

<template>
  <footer>
    <SegmentRenderer segment-key="systemFooter" />
    <div id="legal-container">
      <RouterLink v-if="siteNotice" :to="{ name: 'siteNotice' }">
        {{ $t('admin.system.segments.systemKeys.systemSiteNotice') }}
      </RouterLink>
      <RouterLink v-if="privacyPolicy" :to="{ name: 'privacyPolicy' }">
        {{ $t('admin.system.segments.systemKeys.systemPrivacyPolicy') }}
      </RouterLink>
    </div>
  </footer>
</template>

<style scoped>
footer {
  padding: 1.75rem var(--layout-gap);
  font-size: var(--app-ui-font-size-small);
}

footer > * {
  max-width: var(--max-app-width);
  margin: 0 auto;
}

footer > #legal-container {
  display: flex;
  justify-content: center;
  align-items: center;
  column-gap: 2rem;
  row-gap: 0.5rem;
  flex-wrap: wrap;
  margin-top: 1.5rem;
}

footer > #legal-container a:not(:hover) {
  color: var(--n-font-color);
}
</style>
