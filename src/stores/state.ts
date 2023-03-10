import { ref, computed, watch } from 'vue';
import { defineStore } from 'pinia';
import { useWindowSize } from '@vueuse/core';
import type { TextRead } from '@/openapi';
import Color from 'color';
import { useSettingsStore, usePlatformStore } from '@/stores';
import { useRoute } from 'vue-router';
import type { RouteLocationNormalized } from 'vue-router';

export const useStateStore = defineStore('state', () => {
  // global loading state
  const globalLoading = ref(false);
  const globalLoadingMsg = ref('');
  const globalLoadingProgress = ref(0);
  const startGlobalLoading = () => {
    globalLoading.value = true;
  };
  const finishGlobalLoading = async (delayMs: number = 0, resetLoadingDataDelayMs: number = 0) => {
    await new Promise((resolve) => setTimeout(resolve, delayMs));
    globalLoading.value = false;
    await new Promise((resolve) => setTimeout(resolve, resetLoadingDataDelayMs));
    globalLoadingMsg.value = '...';
    globalLoadingProgress.value = 0;
  };

  // small screen (< 860px)
  const { width } = useWindowSize();
  const smallScreen = computed(() => width.value < 860);

  // current text
  const route = useRoute();
  const pf = usePlatformStore();
  const text = ref<TextRead>();
  watch(route, (after) => {
    if ('text' in after.params && after.params.text) {
      text.value = pf.data?.texts.find((t) => t.slug === after.params.text);
    } else {
      text.value = text.value || pf.data?.texts[0];
    }
  });
  watch(text, () => setPageTitle());

  // current text accent color variants
  const settings = useSettingsStore();
  const accentColor = computed(() => {
    const lighten = settings.theme === 'dark' ? 0.2 : 0.0;
    const base = Color(text.value ? text.value.accentColor : '#18A058').lighten(lighten);
    return {
      base: base.hex(),
      intense: base.saturate(0.5).hex(),
      fade1: base.fade(0.2).hexa(),
      fade2: base.fade(0.4).hexa(),
      fade3: base.fade(0.6).hexa(),
      fade4: base.fade(0.8).hexa(),
      fade5: base.fade(0.9).hexa(),
    };
  });

  // set page title
  function setPageTitle(forRoute?: RouteLocationNormalized) {
    const r = forRoute || route;
    const rTitle = r.meta?.title;
    const tTitle = 'text' in r.params && text.value?.title && ` "${text.value?.title}"`;
    const pfName = pf.data?.info?.platformName ? ` | ${pf.data?.info?.platformName}` : '';
    document.title = `${rTitle || ''}${tTitle || ''}${pfName}`;
  }

  return {
    globalLoading,
    startGlobalLoading,
    finishGlobalLoading,
    globalLoadingMsg,
    globalLoadingProgress,
    smallScreen,
    text,
    accentColor,
    setPageTitle,
  };
});
