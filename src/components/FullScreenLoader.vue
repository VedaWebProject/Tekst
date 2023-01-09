<script setup lang="ts">
import { NSpin } from 'naive-ui';

export interface Props {
  /**
   * Whether or not this loader should be shown
   */
  show: boolean;
  /**
   * Whether to show a spinner or not
   */
  spinner?: boolean;
  /**
   * Transition duration expressed as a
   * [time](https://developer.mozilla.org/en-US/docs/Web/CSS/time) string,
   * e.g. 0.5s or 500ms - default: 0.2s
   */
  transition?: string;
  /**
   * Text to display at the center of the loader
   * (only visible if not overridden by custom elements passed in the component slot)
   */
  text?: string;
}
const props = withDefaults(defineProps<Props>(), {
  show: false,
  spinner: true,
  transition: '500ms',
  text: 'loading...',
});
</script>

<template>
  <Transition name="fade">
    <div class="fullscreen-loader" v-show="props.show">
      <n-spin v-show="props.spinner" size="small" />
      <div class="fullscreen-loader-text">{{ props.text }}</div>
    </div>
  </Transition>
</template>

<style scoped>
.fullscreen-loader {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: #fff;
}
.fullscreen-loader-text {
  padding: 1rem;
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity v-bind('props.transition') ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
