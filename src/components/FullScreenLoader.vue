<script setup lang="ts">
export interface Props {
  /**
   * Whether or not this loader should be shown
   */
  show: boolean;
  /**
   * Transition duration expressed as a
   * [time](https://developer.mozilla.org/en-US/docs/Web/CSS/time) string,
   * e.g. 0.5s or 500ms - default: 0.2s
   */
  duration?: string;
  /**
   * Text to display at the center of the loader
   * (only visible if not overridden by custom elements passed in the component slot)
   */
  text?: string;
}
const props = withDefaults(defineProps<Props>(), {
  show: false,
  duration: '0.2s',
  text: 'loading...',
});
</script>

<template>
  <Transition name="fade">
    <div id="blocking-loader" v-if="props.show">
      <div>
        <slot>{{ props.text }}</slot>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
#blocking-loader {
  position: absolute;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #fff;
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity v-bind('props.duration') ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
