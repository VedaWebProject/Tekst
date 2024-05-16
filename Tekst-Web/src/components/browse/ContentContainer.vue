<script setup lang="ts">
import { NSpin, NIcon, NButton, useThemeVars } from 'naive-ui';
import { ref, watch } from 'vue';
import { useBrowseStore, useStateStore } from '@/stores';
import { computed } from 'vue';
import { $t } from '@/i18n';
import { useElementHover } from '@vueuse/core';
import ContentHeaderWidgetBar from '@/components/browse/ContentHeaderWidgetBar.vue';
import contentComponents from '@/components/content/mappings';
import type { CSSProperties } from 'vue';
import type { AnyResourceRead } from '@/api';
import { NoContentIcon, ExpandIcon, CompressIcon, PublicOffIcon } from '@/icons';
import TranslationDisplay from '@/components/generic/TranslationDisplay.vue';

const props = defineProps<{
  loading?: boolean;
  resource: AnyResourceRead;
}>();

const browse = useBrowseStore();
const state = useStateStore();
const themeVars = useThemeVars();

const contentContainerRef = ref();
const isContentContainerHovered = useElementHover(contentContainerRef, {
  delayEnter: 0,
  delayLeave: 0,
});

const contentCollapsed = ref(!!props.resource.config?.general?.defaultCollapsed);
watch(
  () => browse.reducedView,
  (reduced) => {
    contentCollapsed.value = !reduced && !!props.resource.config?.general?.defaultCollapsed;
  }
);

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
        <div
          class="content-header-title"
          :class="{ reduced: browse.reducedView, b: browse.reducedView }"
        >
          <translation-display v-if="resource.title" :value="resource.title" />
          <n-icon
            v-if="!resource.public"
            :component="PublicOffIcon"
            :color="themeVars.textColorDisabled"
            :title="$t('resources.notPublic')"
          />
        </div>
        <div class="content-header-title-extra">
          {{ headerExtraText }}
        </div>
      </div>
      <content-header-widget-bar :resource="resource" :style="headerWidgetsVisibilityStyle" />
    </div>

    <div v-if="resource.contents?.length" :class="{ 'content-collapsed': contentCollapsed }">
      <!-- content-specific component (that displays the actual content data) -->
      <component
        :is="contentComponents[resource.resourceType]"
        :resource="resource"
        :reduced="browse.reducedView"
      />
    </div>

    <transition>
      <n-spin v-show="loading" class="content-loader" />
    </transition>

    <div
      v-if="resource.config?.general?.defaultCollapsed != null"
      class="content-collapse-btn-wrapper"
    >
      <n-button
        v-if="resource.config?.general?.defaultCollapsed && resource.contents?.length"
        circle
        :color="themeVars.bodyColor"
        :style="{ color: themeVars.textColor1 }"
        :focusable="false"
        class="content-collapse-btn"
        @click="contentCollapsed = !contentCollapsed"
      >
        <template #icon>
          <n-icon :component="contentCollapsed ? ExpandIcon : CompressIcon" />
        </template>
      </n-button>
    </div>
  </div>
</template>

<style scoped>
.content-container {
  padding-top: var(--content-gap);
  padding-bottom: var(--content-gap);
  position: relative;
  font-size: var(--font-size);
}
.content-container.reduced {
  padding-top: 0.3rem;
  padding-bottom: 0.5rem;
  margin: 0;
  box-shadow: none;
  border-radius: 0;
}
.content-container.reduced:first-child {
  border-top-left-radius: var(--border-radius);
  border-top-right-radius: var(--border-radius);
  margin-top: var(--layout-gap);
}
.content-container.reduced:last-child {
  border-bottom-left-radius: var(--border-radius);
  border-bottom-right-radius: var(--border-radius);
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
  margin-bottom: 0.5rem;
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
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: var(--font-size-large);
  color: var(--accent-color);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.content-header-title.reduced {
  font-size: var(--font-size-tiny);
  opacity: 0.8;
}

.content-header-title-extra {
  flex-grow: 2;
  opacity: 0.5;
  font-size: 0.8em;
}

.content-collapsed {
  -webkit-mask-image: linear-gradient(to bottom, black 50%, transparent 100%);
  mask-image: linear-gradient(to bottom, black 50%, transparent 100%);
  max-height: 150px;
  overflow-y: scroll;
}

.content-collapse-btn-wrapper {
  position: absolute;
  left: 0;
  bottom: -16px;
  width: 100%;
  display: flex;
  flex-wrap: nowrap;
  justify-content: center;
  gap: var(--layout-gap);
}

.reduced > .content-collapse-btn-wrapper {
  display: none;
}

.content-collapse-btn:hover {
  color: var(--accent-color) !important;
}

.content-loader {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: var(--content-bg-color);
  border-radius: var(--border-radius);
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
