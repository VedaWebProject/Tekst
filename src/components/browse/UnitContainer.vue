<script setup lang="ts">
import { NSpin } from 'naive-ui';
import MetadataWidget from '@/components/browse/MetadataWidget.vue';

const props = defineProps<{
  title: string;
  layerType: string;
  loading?: boolean;
  active?: boolean;
  meta?: Record<string, string>;
  comment?: string;
}>();
</script>

<template>
  <div v-if="props.active" class="content-block unit-container">
    <div class="unit-container-header">
      <div class="unit-container-header-title">{{ props.title }}</div>
      <div>
        <MetadataWidget :title="props.title" :meta="props.meta" :comment="props.comment" />
      </div>
    </div>
    <slot></slot>
    <Transition>
      <n-spin v-show="props.loading" class="unit-container-loader" />
    </Transition>
  </div>
</template>

<style scoped>
.unit-container {
  position: relative;
  font-size: var(--app-ui-font-size);
}
.unit-container-header {
  display: flex;
  justify-content: flex-end;
  flex-wrap: wrap-reverse;
  column-gap: 12px;
  row-gap: 0px;
  margin-bottom: 0.5rem;
}
.unit-container-header-title {
  flex-grow: 2;
  color: var(--accent-color);
  font-weight: var(--app-ui-font-weight-normal);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.unit-container-loader {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: var(--content-bg-color);
  border-radius: var(--app-ui-border-radius);
}

.unit-container-loader.v-enter-active,
.unit-container-loader.v-leave-active {
  transition: opacity 0.1s ease;
}

.unit-container-loader.v-enter-from,
.unit-container-loader.v-leave-to {
  opacity: 0;
}
</style>
