<script setup lang="ts">
import { NFlex, NSpin, NIcon, NButton, useThemeVars } from 'naive-ui';
import { ref, watch } from 'vue';
import { useBrowseStore, useStateStore } from '@/stores';
import { computed } from 'vue';
import { $t } from '@/i18n';
import { useElementHover } from '@vueuse/core';
import ContentHeaderWidgetBar from '@/components/browse/ContentHeaderWidgetBar.vue';
import contentComponents from '@/components/content/mappings';
import type { AnyResourceRead } from '@/api';
import { NoContentIcon, ExpandIcon, CompressIcon, PublicOffIcon } from '@/icons';
import TranslationDisplay from '@/components/generic/TranslationDisplay.vue';
import { MergeIcon } from '@/icons';

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

const contentCollapsed = ref(!!props.resource.config.general.defaultCollapsed);
watch(
  () => browse.reducedView,
  (reduced) => {
    contentCollapsed.value = !reduced && !!props.resource.config.general.defaultCollapsed;
  },
  { immediate: true }
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
const headerWidgetsOpacity = computed<number>(() =>
  isContentContainerHovered.value || state.isTouchDevice ? 1 : browse.reducedView ? 0 : 0.2
);
const hasContent = computed(() => props.resource.contents?.length);
const show = computed(() => props.resource.active && (hasContent.value || !browse.reducedView));
const fromChildLevel = computed(
  () => props.resource.level - 1 === browse.level && props.resource.config.common.showOnParentLevel
);
</script>

<template>
  <div
    v-if="show"
    ref="contentContainerRef"
    class="content-block content-container"
    :class="{ reduced: browse.reducedView, empty: !hasContent && !fromChildLevel }"
    :title="contentContainerTitle"
  >
    <div class="content-header mb-sm" :class="browse.reducedView ? 'reduced' : ''">
      <n-icon v-if="!hasContent && !fromChildLevel" :component="NoContentIcon" />
      <div class="content-header-title-container">
        <div
          class="content-header-title"
          :class="{ reduced: browse.reducedView, b: browse.reducedView }"
        >
          <span>
            <translation-display v-if="resource.title" :value="resource.title" />
          </span>
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
      <content-header-widget-bar
        :resource="resource"
        :opacity="headerWidgetsOpacity"
        :small-screen="state.smallScreen"
      />
    </div>

    <n-spin :show="loading" size="small">
      <div
        v-if="hasContent"
        class="content"
        :class="{ 'content-collapsed': contentCollapsed, 'content-loading': loading }"
      >
        <!-- content-specific component (that displays the actual content data) -->
        <component
          :is="contentComponents[resource.resourceType]"
          :resource="resource"
          :reduced="browse.reducedView"
        />
      </div>
      <n-flex v-else-if="fromChildLevel" align="center" size="small" class="translucent text-tiny">
        {{
          $t('browse.contents.showCombinedContents', {
            level: state.textLevelLabels[resource.level],
          })
        }}
        <n-icon :component="MergeIcon" />
      </n-flex>
    </n-spin>

    <n-button
      v-if="
        resource.config.general.defaultCollapsed && !browse.reducedView && resource.contents?.length
      "
      text
      block
      class="mt-sm"
      :focusable="false"
      @click="contentCollapsed = !contentCollapsed"
    >
      <template #icon>
        <n-icon :component="contentCollapsed ? ExpandIcon : CompressIcon" />
      </template>
      {{ contentCollapsed ? $t('general.expandAction') : $t('general.collapseAction') }}
    </n-button>
  </div>
</template>

<style scoped>
.content-container {
  padding-top: var(--gap-md);
  padding-bottom: var(--gap-md);
  font-size: var(--font-size);
}

.content-container.reduced {
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
  margin: 0;
  box-shadow: none;
  border-radius: 0;
}

.content-container.reduced:first-child {
  border-top-left-radius: var(--border-radius);
  border-top-right-radius: var(--border-radius);
  margin-top: var(--gap-lg);
}

.content-container.reduced:last-child {
  border-bottom-left-radius: var(--border-radius);
  border-bottom-right-radius: var(--border-radius);
  margin-bottom: var(--gap-lg);
}

.content-container.reduced:not(:first-child) {
  border-top: 1px solid var(--main-bg-color);
  margin-bottom: 0;
}

.content-container.empty {
  background-color: var(--main-bg-color);
  border: 2px dashed var(--main-bg-color);
  box-shadow: none;
  padding: 12px var(--gap-lg);
}

.content-container.empty > .content-header {
  margin-bottom: 0;
  opacity: 0.6;
}

.content-header {
  display: flex;
  align-items: center;
  flex-wrap: nowrap;
  column-gap: 12px;
  row-gap: 0px;
}

.content-header.reduced {
  margin-bottom: 0;
}

.content-header-title-container {
  display: flex;
  align-items: baseline;
  flex-wrap: nowrap;
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

.content-header-title > span {
  white-space: wrap;
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

.content {
  transition: opacity 0.2s ease;
}

.content.content-loading {
  opacity: 0;
}
</style>
