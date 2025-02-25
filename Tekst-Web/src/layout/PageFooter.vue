<script setup lang="ts">
import SegmentRenderer from '@/components/SegmentRenderer.vue';
import { useStateStore } from '@/stores';
import { computed } from 'vue';

const state = useStateStore();
const siteNotice = computed(
  () => !!state.pf?.systemSegments.find((s) => s.key === 'systemSiteNotice')
);
const privacyPolicy = computed(
  () => !!state.pf?.systemSegments.find((s) => s.key === 'systemPrivacyPolicy')
);
</script>

<template>
  <footer>
    <segment-renderer segment-key="systemFooterUpper" />
    <segment-renderer segment-key="systemFooterLower" />
    <div v-if="siteNotice || privacyPolicy" id="legal-container">
      <router-link v-if="siteNotice" :to="{ name: 'siteNotice' }">
        {{ $t('admin.segments.systemKeys.systemSiteNotice') }}
      </router-link>
      <router-link v-if="privacyPolicy" :to="{ name: 'privacyPolicy' }">
        {{ $t('admin.segments.systemKeys.systemPrivacyPolicy') }}
      </router-link>
    </div>
    <div v-if="state.pf?.state.showTekstFooterHint" class="tekst-hint text-tiny">
      {{ $t('general.tekstFooterHint') }}
      <a
        href="http://github.com/VedaWebProject/Tekst"
        target="_blank"
        rel="external nofollow"
        class="b"
        :title="`${state.pf.tekst?.name} – ${state.pf.tekst?.description} (${state.pf.tekst?.version})`"
      >
        {{ state.pf.tekst?.name }}
      </a>
    </div>
  </footer>
</template>

<style scoped>
footer {
  padding: var(--gap-lg);
  font-size: var(--font-size-small);
}

footer > * {
  max-width: var(--max-app-width);
  margin: var(--gap-lg) auto 0 auto;
}

footer > *:first-child {
  margin-top: var(--gap-md);
}

footer > #legal-container {
  display: flex;
  justify-content: center;
  align-items: center;
  column-gap: 2rem;
  row-gap: 0.5rem;
  flex-wrap: wrap;
}

footer .tekst-hint {
  text-align: center;
}
</style>
