<script setup lang="ts">
import SegmentRenderer from '@/components/SegmentRenderer.vue';
import TranslationDisplay from '@/components/generic/TranslationDisplay.vue';
import { usePlatformData } from '@/composables/platformData';
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
    <segment-renderer segment-key="systemFooter" />
    <div v-if="pfData?.settings.showFooterInfo">
      <span>
        {{ pfData?.settings.infoPlatformName }}
      </span>
      <span v-if="pfData?.settings.infoSubtitle?.length" style="font-style: italic">
        – <translation-display :value="pfData?.settings.infoSubtitle" />
      </span>
    </div>
    <div v-if="siteNotice || privacyPolicy" id="legal-container">
      <router-link v-if="siteNotice" :to="{ name: 'siteNotice' }">
        {{ $t('admin.system.segments.systemKeys.systemSiteNotice') }}
      </router-link>
      <router-link v-if="privacyPolicy" :to="{ name: 'privacyPolicy' }">
        {{ $t('admin.system.segments.systemKeys.systemPrivacyPolicy') }}
      </router-link>
    </div>
  </footer>
</template>

<style scoped>
footer {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--content-gap);
  padding: var(--layout-gap);
  font-size: var(--font-size-small);
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
}
</style>
