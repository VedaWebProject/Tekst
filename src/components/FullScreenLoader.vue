<script setup lang="ts">
import { computed } from 'vue';
import { NProgress } from 'naive-ui';

export interface Props {
  /**
   * Whether or not this loader should be shown
   */
  show: boolean;
  /**
   * Text to display at the center of the loader
   * (only visible if not overridden by custom elements passed in the component slot)
   */
  text?: string;
  /**
   * Whether to show a spinner or not
   */
  showProgress?: boolean;
  /**
   * Progres percentage
   */
  progress?: number;
  /**
   * Progress bar color
   */
  progressColor?: string;
  /**
   * Transition duration expressed as a
   * [time](https://developer.mozilla.org/en-US/docs/Web/CSS/time) string,
   * e.g. 0.5s or 500ms - default: 0.2s
   */
  transition?: string;
}
const props = withDefaults(defineProps<Props>(), {
  show: false,
  text: 'loading...',
  showProgress: true,
  progress: 0,
  progressColor: '#444',
  transition: '500ms',
});

const progress = computed(() =>
  props.progress !== undefined ? Math.abs(props.progress) * 100 : 0
);
</script>

<template>
  <Transition name="fade">
    <div class="fullscreen-loader" v-show="props.show">
      <div class="fullscreen-loader-text">{{ props.text }}</div>
      <n-progress
        v-show="props.showProgress && props.progress !== undefined"
        type="line"
        :percentage="progress"
        :show-indicator="false"
        :height="4"
        color="#18A058"
        border-radius="0"
        processing
      />
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
  padding: 1em;
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
