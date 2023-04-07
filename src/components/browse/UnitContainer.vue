<script setup lang="ts">
import { NSpin } from 'naive-ui';
import MetadataWidget from '@/components/browse/widgets/MetadataWidget.vue';
import { type Component, defineAsyncComponent } from 'vue';

const props = defineProps<{
  loading?: boolean;
  layer: Record<string, any>;
}>();

const UNIT_COMPONENTS: Record<string, Component> = {
  plaintext: defineAsyncComponent(() => import('@/components/browse/units/PlaintextUnit.vue')),
};

const UNIT_WIDGETS: Record<string, Component> = {
  deeplLinks: defineAsyncComponent(
    () => import('@/components/browse/widgets/DeepLLinksWidget.vue')
  ),
};
</script>

<template>
  <div v-if="props.layer.active && props.layer.unit" class="content-block unit-container">
    <div class="unit-container-header">
      <div class="unit-container-header-title">{{ props.layer.title }}</div>
      <div class="unit-container-header-widgets">
        <!-- config-specific widgets -->
        <template
          v-for="(configSection, configSectionKey) in props.layer.config"
          :key="configSectionKey"
        >
          <component
            v-if="configSectionKey in UNIT_WIDGETS"
            :is="UNIT_WIDGETS[configSectionKey]"
            :unit-data="props.layer.unit"
            :widget-config="configSection"
          />
        </template>
        <!-- generic unit widgets -->
        <MetadataWidget
          v-if="props.layer.meta || props.layer.comment"
          :title="props.layer.title"
          :meta="props.layer.meta"
          :comment="props.layer.comment"
        />
      </div>
    </div>

    <!-- unit-specific component (that displays the actual unit data) -->
    <component
      :is="UNIT_COMPONENTS[props.layer.layerType]"
      :unit-data="props.layer.unit"
      :layer-config="props.layer.config"
    />

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

.unit-container-header-widgets {
  display: flex;
  align-items: center;
  flex-wrap: nowrap;
  gap: 8px;
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
