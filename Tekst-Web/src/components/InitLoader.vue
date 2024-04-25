<script setup lang="ts">
import { useStateStore } from '@/stores';
import { useLoadingBar } from 'naive-ui';
import { computed, onBeforeMount } from 'vue';
import { useRouter } from 'vue-router';

const props = withDefaults(
  defineProps<{
    show: boolean;
    text?: string;
    darkMode?: boolean;
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
    transition: '500ms',
  }
);

const state = useStateStore();
const loadingBar = useLoadingBar();
const router = useRouter();

const dynamicStyle = computed(() => ({
  color: props.darkMode ? '#fff' : '#444',
  backgroundColor: props.darkMode ? '#232323' : '#fff',
}));

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
    <div v-if="props.show" class="global-loader-container">
      <div class="global-loader" :style="dynamicStyle">
        <div
          class="global-loader-text"
          :style="{ visibility: state.initLoadingProgress < 1 ? 'visible' : 'hidden' }"
        >
          {{ props.text }}
        </div>
      </div>
    </div>
  </transition>
</template>

<style scoped>
.global-loader-container {
  background-color: #fff;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 3;
  overflow: hidden;
}
.global-loader {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.global-loader-text {
  font-size: var(--font-size-small);
  height: 2em;
  width: 100%;
  text-align: center;
  transition: 0.5s;
}

.fade-leave-active {
  transition: opacity v-bind('props.transition') ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
