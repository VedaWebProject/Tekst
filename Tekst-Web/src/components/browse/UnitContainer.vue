<script setup lang="ts">
import { NSpin, NIcon } from 'naive-ui';
import { ref } from 'vue';
import { useBrowseStore, useStateStore } from '@/stores';
import { computed } from 'vue';
import { $t } from '@/i18n';
import { useElementHover } from '@vueuse/core';
import UnitHeaderWidgetBar from '@/components/browse/UnitHeaderWidgetBar.vue';
import unitComponents from '@/components/browse/units/mappings';

import FolderOffOutlined from '@vicons/material/FolderOffOutlined';
import type { CSSProperties } from 'vue';

const props = defineProps<{
  loading?: boolean;
  layer: Record<string, any>;
}>();

const browse = useBrowseStore();
const state = useStateStore();

const unitContainerRef = ref();
const isUnitContainerHovered = useElementHover(unitContainerRef, { delayEnter: 0, delayLeave: 0 });

const headerMiddleText = computed(() =>
  props.layer.level !== browse.level
    ? `(${$t('browse.location.level')}: ${state.textLevelLabels[props.layer.level]})`
    : ''
);

const emptyUnitStyle = {
  backgroundColor: 'var(--main-bg-color)',
  border: '2px dashed var(--main-bg-color)',
  boxShadow: 'none',
  padding: '12px var(--layout-gap)',
};

const altUnitContainerStyle = computed(() => (!props.layer.units.length ? emptyUnitStyle : {}));
const unitContainerTitle = computed(() =>
  !props.layer.units.length ? $t('browse.locationLayerNoData') : undefined
);
const headerWidgetsVisibilityStyle = computed<CSSProperties>(() => ({
  opacity: isUnitContainerHovered.value || state.isTouchDevice ? 1 : 0.2,
}));
</script>

<template>
  <div
    v-if="layer.active && (layer.units.length || !browse.reducedView)"
    ref="unitContainerRef"
    class="content-block unit-container"
    :style="altUnitContainerStyle"
    :title="unitContainerTitle"
  >
    <div class="unit-header">
      <n-icon v-if="!layer.units.length" :component="FolderOffOutlined" />
      <div class="unit-header-title-container">
        <div class="unit-header-title">{{ layer.title }}</div>
        <div class="unit-header-title-extra">
          {{ headerMiddleText }}
        </div>
      </div>
      <UnitHeaderWidgetBar :layer="layer" :style="headerWidgetsVisibilityStyle" />
    </div>
    <!-- unit-specific component (that displays the actual unit data) -->
    <component
      :is="unitComponents[layer.layerType]"
      v-if="layer.units.length"
      :layer="layer"
      :layer-config="layer.config"
    />
    <Transition>
      <n-spin v-show="loading" class="unit-loader" />
    </Transition>
  </div>
</template>

<style scoped>
.unit-container {
  position: relative;
  font-size: var(--app-ui-font-size);
}
.unit-header {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  column-gap: 12px;
  row-gap: 0px;
}

.unit-header-title-container {
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  flex-grow: 2;
  column-gap: 12px;
}

.unit-header-title {
  color: var(--accent-color);
  font-weight: var(--app-ui-font-weight-normal);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.unit-header-title-extra {
  flex-grow: 2;
  opacity: 0.5;
  font-size: 0.8em;
}

.unit-loader {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: var(--content-bg-color);
  border-radius: var(--app-ui-border-radius);
}

.unit-loader.v-enter-active,
.unit-loader.v-leave-active {
  transition: opacity 0.1s ease;
}

.unit-loader.v-enter-from,
.unit-loader.v-leave-to {
  opacity: 0;
}
</style>
