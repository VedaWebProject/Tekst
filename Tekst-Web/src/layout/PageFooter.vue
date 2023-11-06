<script setup lang="ts">
import { NButton } from 'naive-ui';
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
      <n-button v-if="siteNotice" text @click="() => $router.push('/site-notice')">{{
        $t('admin.system.segments.systemKeys.systemSiteNotice')
      }}</n-button>
      <n-button v-if="privacyPolicy" text @click="() => $router.push('/privacy-policy')">{{
        $t('admin.system.segments.systemKeys.systemPrivacyPolicy')
      }}</n-button>
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
</style>
