<script setup lang="ts">
import SegmentRenderer from '@/components/SegmentRenderer.vue';
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
    <div v-if="siteNotice || privacyPolicy" id="legal-container">
      <router-link v-if="siteNotice" :to="{ name: 'siteNotice' }">
        {{ $t('admin.system.segments.systemKeys.systemSiteNotice') }}
      </router-link>
      <router-link v-if="privacyPolicy" :to="{ name: 'privacyPolicy' }">
        {{ $t('admin.system.segments.systemKeys.systemPrivacyPolicy') }}
      </router-link>
    </div>
    <div v-if="pfData?.state.showTekstFooterHint" class="text-tiny">
      {{ $t('general.tekstFooterHint') }}
      <a
        href="http://github.com/VedaWebProject/Tekst"
        target="_blank"
        rel="external nofollow"
        style="font-weight: var(--font-weight-bold)"
        :title="`${pfData.tekst?.name} – ${pfData.tekst?.description} (${pfData.tekst?.version})`"
      >
        {{ pfData.tekst?.name }}
      </a>
    </div>
  </footer>
</template>

<style scoped>
footer {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--gap-lg);
  padding: var(--gap-lg);
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
