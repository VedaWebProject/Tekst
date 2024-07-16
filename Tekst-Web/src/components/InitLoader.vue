<script setup lang="ts">
import { useLogo } from '@/composables/logo';
import { usePlatformData } from '@/composables/platformData';
import { useStateStore } from '@/stores';
import { useLoadingBar } from 'naive-ui';
import { onBeforeMount } from 'vue';
import { useRouter } from 'vue-router';
import { NProgress, NFlex } from 'naive-ui';

const props = withDefaults(
  defineProps<{
    show: boolean;
    text?: string;
    darkMode?: boolean;
    progress?: number;
    /**
     * Transition duration expressed as a
     * [time](https://developer.mozilla.org/en-US/docs/Web/CSS/time) string,
     * e.g. 0.5s or 500ms - default: 0.2s
     */
    transition?: string;
  }>(),
  {
    show: true,
    text: 'loading...',
    darkMode: false,
    progress: 0,
    transition: '500ms',
  }
);

const { pageLogo } = useLogo();
const state = useStateStore();
const { pfData } = usePlatformData();

const loadingBar = useLoadingBar();
const router = useRouter();

// hook in loading bar
onBeforeMount(() => {
  router.beforeEach(() => {
    !state.initLoading && loadingBar.start();
  });
  router.afterEach(() => {
    loadingBar.finish();
  });
  router.onError(() => {
    loadingBar.error();
  });
});
</script>

<template>
  <transition name="fade">
    <div v-if="show" class="global-loader-container">
      <n-flex vertical align="center" justify="flex-end" size="large" class="global-loader-top">
        <img
          class="global-loader-logo"
          :src="pageLogo"
          :style="{
            opacity: pageLogo && pfData?.settings.showLogoOnLoadingScreen ? 1 : 0,
          }"
        />
        <div class="text-huge">{{ pfData?.settings.platformName }}</div>
        <n-progress
          type="line"
          :percentage="progress * 100"
          :height="2"
          :show-indicator="false"
          :border-radius="0"
          size="large"
          color="var(--text-color)"
          rail-color="transparent"
          style="opacity: 0.3"
        />
      </n-flex>
      <n-flex
        vertical
        align="center"
        justify="flex-start"
        size="large"
        class="global-loader-bottom"
      >
        <div class="global-loader-text" :style="{ opacity: text ? 1 : 0 }">
          {{ text }}
        </div>
      </n-flex>
    </div>
  </transition>
</template>

<style scoped>
.global-loader-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 3;
  overflow: hidden;
  background-color: var(--base-color);
}

.global-loader-top {
  width: 100%;
  height: 50%;
  background-color: var(--content-bg-color);
}

.global-loader-bottom {
  width: 100%;
  height: 50%;
  padding-top: var(--layout-gap);
  background-color: var(--main-bg-color);
}

.global-loader-logo {
  height: 4rem;
  width: auto;
  transition: opacity 0.2s;
}

.global-loader-text {
  font-size: var(--font-size-small);
  height: 2em;
  width: 100%;
  text-align: center;
  transition: opacity 0.2s;
}

.fade-leave-active {
  transition: opacity v-bind('props.transition') ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
