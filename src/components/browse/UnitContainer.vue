<script setup lang="ts">
import { NSpin } from 'naive-ui';
import LayerInfoWidget from '@/components/browse/widgets/LayerInfoWidget.vue';
import { type Component, defineAsyncComponent } from 'vue';
import { useBrowseStore, useStateStore } from '@/stores';
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';

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

const browse = useBrowseStore();
const state = useStateStore();
const { t } = useI18n({ useScope: 'global' });

const headerMiddleText = computed(() =>
  props.layer.level !== browse.level
    ? t('browse.units.fromHigherLevel', { level: state.textLevelLabels[props.layer.level] })
    : ''
);
</script>

<template>
  <div v-if="layer.active && layer.unit" class="content-block unit-container">
    <div class="unit-container-header">
      <div class="unit-container-header-title-container">
        <div class="unit-container-header-title">{{ layer.title }}</div>
        <div class="unit-container-header-title-extra">
          {{ headerMiddleText }}
        </div>
      </div>
      <div class="unit-container-header-widgets">
        <!-- config-specific widgets -->
        <template v-for="(configSection, configSectionKey) in layer.config" :key="configSectionKey">
          <component
            v-if="configSectionKey in UNIT_WIDGETS"
            :is="UNIT_WIDGETS[configSectionKey]"
            :unit-data="layer.unit"
            :widget-config="configSection"
          />
        </template>
        <!-- generic unit widgets -->
        <LayerInfoWidget :data="layer" />
      </div>
    </div>

    <!-- unit-specific component (that displays the actual unit data) -->
    <component
      :is="UNIT_COMPONENTS[layer.layerType]"
      :unit-data="layer.unit"
      :layer-config="layer.config"
    />

    <Transition>
      <n-spin v-show="loading" class="unit-container-loader" />
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
  align-items: flex-start;
  flex-wrap: wrap;
  column-gap: 12px;
  row-gap: 0px;
  margin-bottom: 0.5rem;
}

.unit-container-header-title-container {
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  flex-grow: 2;
  column-gap: 12px;
}

.unit-container-header-title {
  color: var(--accent-color);
  font-weight: var(--app-ui-font-weight-normal);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.unit-container-header-title-extra {
  flex-grow: 2;
  opacity: 0.5;
  font-size: 0.8em;
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
