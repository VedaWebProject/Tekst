<script setup lang="ts">
import TranslationDisplay from '@/components/generic/TranslationDisplay.vue';
import PrimaryNavBar from '@/components/navigation/PrimaryNavBar.vue';
import TextSelect from '@/components/navigation/TextSelect.vue';
import { usePlatformData } from '@/composables/platformData';
import { useStateStore } from '@/stores';
import { useThemeVars } from 'naive-ui';
import { useRoute } from 'vue-router';

const state = useStateStore();
const route = useRoute();
const { pfData } = usePlatformData();
const themeVars = useThemeVars();
</script>

<template>
  <header>
    <primary-nav-bar />
    <div class="accent-color-bg" style="min-height: 12px" :style="{ color: themeVars.baseColor }">
      <div
        v-if="route.meta.isTextSpecific || pfData?.settings.alwaysShowTextInfo"
        id="current-text"
      >
        <text-select />
        <span
          v-if="!state.smallScreen && state.text?.subtitle?.length"
          class="current-text-subtitle"
        >
          <translation-display :value="state.text?.subtitle" />
        </span>
      </div>
    </div>
  </header>
</template>

<style scoped>
#current-text {
  --current-text-height: 64px;
  height: var(--current-text-height);
  display: flex;
  column-gap: 24px;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  padding: 0 var(--layout-gap);
  max-width: var(--max-app-width);
  margin: 0 auto;
  font-size: var(--font-size-large);
}

#current-text .current-text-subtitle {
  filter: opacity(0.6);
}
</style>
