<script setup lang="ts">
import { NSpin, NIcon } from 'naive-ui';
import LayerInfoWidget from '@/components/browse/widgets/LayerInfoWidget.vue';
import LayerDeactivateWidget from '@/components/browse/widgets/LayerDeactivateWidget.vue';
import { type Component, defineAsyncComponent } from 'vue';
import { useBrowseStore, useStateStore } from '@/stores';
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';

import FolderOffOutlined from '@vicons/material/FolderOffOutlined';

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

const emptyUnitStyle = {
  backgroundColor: 'transparent',
  border: '3px dashed var(--content-bg-color)',
  boxShadow: 'none',
  padding: '12px var(--layout-gap)',
};

const altUnitContainerStyle = computed(() => (!props.layer.unit ? emptyUnitStyle : {}));
const unitContainerTitle = computed(() =>
  !props.layer.unit ? t('browse.locationLayerNoData') : undefined
);
</script>

<template>
  <div
    v-if="layer.active && (layer.unit || !browse.reducedView)"
    class="content-block unit-container"
    :style="altUnitContainerStyle"
    :title="unitContainerTitle"
  >
    <div class="unit-container-header">
      <n-icon v-if="!layer.unit" :component="FolderOffOutlined" />
      <div class="unit-container-header-title-container">
        <div class="unit-container-header-title">{{ layer.title }}</div>
        <div class="unit-container-header-title-extra">
          {{ headerMiddleText }}
        </div>
      </div>
      <div class="unit-container-header-widgets">
        <!-- config-specific widgets -->
        <template v-if="layer.unit">
          <template
            v-for="(configSection, configSectionKey) in layer.config"
            :key="configSectionKey"
          >
            <component
              v-if="configSectionKey in UNIT_WIDGETS"
              :is="UNIT_WIDGETS[configSectionKey]"
              :unit-data="layer.unit"
              :widget-config="configSection"
            />
          </template>
        </template>
        <!-- generic unit widgets -->
        <LayerInfoWidget :layer="layer" />
        <LayerDeactivateWidget :layer="layer" />
      </div>
    </div>

    <!-- unit-specific component (that displays the actual unit data) -->
    <component
      v-if="layer.unit"
      :is="UNIT_COMPONENTS[layer.layerType]"
      :unit-data="layer.unit"
      :layer-config="layer.config"
      style="margin-top: 0.5rem"
    />

    <!--  -->

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
  align-items: center;
  flex-wrap: wrap;
  column-gap: 12px;
  row-gap: 0px;
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
