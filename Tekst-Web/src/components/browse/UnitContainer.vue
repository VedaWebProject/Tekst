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
import type { AnyResourceRead } from '@/api';

const props = defineProps<{
  loading?: boolean;
  resource: AnyResourceRead;
}>();

const browse = useBrowseStore();
const state = useStateStore();

const unitContainerRef = ref();
const isUnitContainerHovered = useElementHover(unitContainerRef, { delayEnter: 0, delayLeave: 0 });

const headerExtraText = computed(() => {
  if (!browse.loadingResources && props.resource.level !== browse.level) {
    const level = state.textLevelLabels[props.resource.level];
    return level
      ? `(${$t('browse.location.level')}: ${state.textLevelLabels[props.resource.level]})`
      : '';
  } else {
    return '';
  }
});

const unitContainerTitle = computed(() =>
  !props.resource.units?.length ? $t('browse.locationResourceNoData') : undefined
);
const headerWidgetsVisibilityStyle = computed<CSSProperties>(() => ({
  opacity: isUnitContainerHovered.value || state.isTouchDevice ? 1 : browse.reducedView ? 0 : 0.2,
}));
</script>

<template>
  <div
    v-if="resource.active && (resource.units?.length || !browse.reducedView)"
    ref="unitContainerRef"
    class="content-block unit-container"
    :class="{ reduced: browse.reducedView, empty: !resource.units?.length }"
    :title="unitContainerTitle"
  >
    <div class="unit-header" :class="browse.reducedView ? 'reduced' : ''">
      <n-icon v-if="!resource.units?.length" :component="FolderOffOutlined" />
      <div class="unit-header-title-container">
        <div class="unit-header-title" :class="browse.reducedView ? 'reduced' : ''">
          {{ resource.title }}
        </div>
        <div class="unit-header-title-extra">
          {{ headerExtraText }}
        </div>
      </div>
      <UnitHeaderWidgetBar :resource="resource" :style="headerWidgetsVisibilityStyle" />
    </div>
    <!-- unit-specific component (that displays the actual unit data) -->
    <component
      :is="unitComponents[resource.resourceType]"
      v-if="resource.units?.length"
      :resource="resource"
      :reduced="browse.reducedView"
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
.unit-container.reduced {
  padding-top: 0.3rem;
  padding-bottom: 0.3rem;
  margin: 0;
  box-shadow: none;
  border-radius: 0;
}
.unit-container.reduced:first-child {
  border-top-left-radius: var(--app-ui-border-radius);
  border-top-right-radius: var(--app-ui-border-radius);
  margin-top: var(--layout-gap);
}
.unit-container.reduced:last-child {
  border-bottom-left-radius: var(--app-ui-border-radius);
  border-bottom-right-radius: var(--app-ui-border-radius);
  margin-bottom: var(--layout-gap);
}
.unit-container.empty {
  background-color: var(--main-bg-color);
  border: 2px dashed var(--main-bg-color);
  box-shadow: none;
  padding: 12px var(--layout-gap);
}
.unit-container.empty > .unit-header {
  margin-bottom: 0;
}
.unit-header {
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  column-gap: 12px;
  row-gap: 0px;
}
.unit-header.reduced {
  margin-bottom: 0;
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

.unit-header-title.reduced {
  font-size: var(--app-ui-font-size-tiny);
  font-weight: var(--app-ui-font-weight-light);
  opacity: 0.8;
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
