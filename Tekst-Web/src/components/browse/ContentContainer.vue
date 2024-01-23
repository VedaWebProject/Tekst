<script setup lang="ts">
import { NSpin, NIcon } from 'naive-ui';
import { ref } from 'vue';
import { useBrowseStore, useStateStore } from '@/stores';
import { computed } from 'vue';
import { $t } from '@/i18n';
import { useElementHover } from '@vueuse/core';
import ContentHeaderWidgetBar from '@/components/browse/ContentHeaderWidgetBar.vue';
import contentComponents from '@/components/content/mappings';
import type { CSSProperties } from 'vue';
import type { AnyResourceRead } from '@/api';

import { NoContentIcon } from '@/icons';

const props = defineProps<{
  loading?: boolean;
  resource: AnyResourceRead;
}>();

const browse = useBrowseStore();
const state = useStateStore();

const contentContainerRef = ref();
const isContentContainerHovered = useElementHover(contentContainerRef, {
  delayEnter: 0,
  delayLeave: 0,
});

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

const contentContainerTitle = computed(() =>
  !props.resource.contents?.length ? $t('browse.locationResourceNoData') : undefined
);
const headerWidgetsVisibilityStyle = computed<CSSProperties>(() => ({
  opacity:
    isContentContainerHovered.value || state.isTouchDevice ? 1 : browse.reducedView ? 0 : 0.2,
}));
</script>

<template>
  <div
    v-if="resource.active && (resource.contents?.length || !browse.reducedView)"
    ref="contentContainerRef"
    class="content-block content-container"
    :class="{ reduced: browse.reducedView, empty: !resource.contents?.length }"
    :title="contentContainerTitle"
  >
    <div class="content-header" :class="browse.reducedView ? 'reduced' : ''">
      <n-icon v-if="!resource.contents?.length" :component="NoContentIcon" />
      <div class="content-header-title-container">
        <div class="content-header-title" :class="browse.reducedView ? 'reduced' : ''">
          {{ resource.title }}
        </div>
        <div class="content-header-title-extra">
          {{ headerExtraText }}
        </div>
      </div>
      <ContentHeaderWidgetBar :resource="resource" :style="headerWidgetsVisibilityStyle" />
    </div>
    <!-- content-specific component (that displays the actual content data) -->
    <component
      :is="contentComponents[resource.resourceType]"
      v-if="resource.contents?.length"
      :resource="resource"
      :reduced="browse.reducedView"
    />
    <Transition>
      <n-spin v-show="loading" class="content-loader" />
    </Transition>
  </div>
</template>

<style scoped>
.content-container {
  position: relative;
  font-size: var(--app-ui-font-size);
}
.content-container.reduced {
  padding-top: 0.3rem;
  padding-bottom: 0.5rem;
  margin: 0;
  box-shadow: none;
  border-radius: 0;
}
.content-container.reduced:first-child {
  border-top-left-radius: var(--app-ui-border-radius);
  border-top-right-radius: var(--app-ui-border-radius);
  margin-top: var(--layout-gap);
}
.content-container.reduced:last-child {
  border-bottom-left-radius: var(--app-ui-border-radius);
  border-bottom-right-radius: var(--app-ui-border-radius);
  margin-bottom: var(--layout-gap);
}
.content-container.reduced:not(:first-child) {
  border-top: 1px solid var(--main-bg-color);
  margin-bottom: 0;
}
.content-container.empty {
  background-color: var(--main-bg-color);
  border: 2px dashed var(--main-bg-color);
  box-shadow: none;
  padding: 12px var(--layout-gap);
}
.content-container.empty > .content-header {
  margin-bottom: 0;
}
.content-header {
  margin: 0.25rem 0 0.5rem 0;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  column-gap: 12px;
  row-gap: 0px;
}
.content-header.reduced {
  margin-bottom: 0;
}

.content-header-title-container {
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  flex-grow: 2;
  column-gap: 12px;
}

.content-header-title {
  color: var(--accent-color);
  font-weight: var(--app-ui-font-weight-normal);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.content-header-title.reduced {
  font-size: var(--app-ui-font-size-tiny);
  font-weight: var(--app-ui-font-weight-light);
  opacity: 0.8;
}

.content-header-title-extra {
  flex-grow: 2;
  opacity: 0.5;
  font-size: 0.8em;
}

.content-loader {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: var(--content-bg-color);
  border-radius: var(--app-ui-border-radius);
}

.content-loader.v-enter-active,
.content-loader.v-leave-active {
  transition: opacity 0.1s ease;
}

.content-loader.v-enter-from,
.content-loader.v-leave-to {
  opacity: 0;
}
</style>
