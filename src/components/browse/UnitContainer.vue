<script setup lang="ts">
import { NSpin } from 'naive-ui';

const props = defineProps<{
  title?: string;
  loading?: boolean;
}>();
</script>

<template>
  <div class="content-block" style="position: relative">
    <div class="unit-container-title">{{ props.title }}</div>
    <slot></slot>
    <Transition>
      <n-spin v-if="props.loading" class="unit-container-loader" />
    </Transition>
  </div>
</template>

<style scoped>
.unit-container-title {
  color: var(--accent-color);
  font-size: var(--app-ui-font-size-small);
  font-weight: var(--app-ui-font-weight-normal);
  margin-bottom: 12px;
}

.unit-container-loader {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: var(--content-bg-color);
  opacity: 0.9;
  border-radius: var(--app-ui-border-radius);
  transition: 0.3s;
}

.unit-container-loader.v-enter-active,
.unit-container-loader.v-leave-active {
  transition: opacity 0.2s ease;
}

.unit-container-loader.v-enter-from,
.unit-container-loader.v-leave-to {
  opacity: 0;
}
</style>
