<script setup lang="ts">
import type { AnyResourceRead } from '@/api';
import ContentHeaderWidgetBar from '@/components/browse/ContentHeaderWidgetBar.vue';
import CollapsableContent from '@/components/CollapsableContent.vue';
import contentComponents from '@/components/content/mappings';
import { $t } from '@/i18n';
import {
  HourglassIcon,
  LevelsIcon,
  MergeIcon,
  NoContentIcon,
  ProposedIcon,
  PublicOffIcon,
  WarningIcon,
} from '@/icons';
import { useBrowseStore, useStateStore } from '@/stores';
import { pickTranslation } from '@/utils';
import { useElementHover } from '@vueuse/core';
import { NFlex, NIcon, NSpin, NTag, useThemeVars } from 'naive-ui';
import { computed, ref, watch } from 'vue';

const props = defineProps<{
  loading?: boolean;
  resource: AnyResourceRead;
}>();

const browse = useBrowseStore();
const state = useStateStore();
const themeVars = useThemeVars();

const contentsLoaded = computed(() => !!props.resource.contents?.length);
const onChildLevel = computed(() => props.resource.level - 1 === browse.level);
const contentContextLoaded = computed(() => contentsLoaded.value && onChildLevel.value);

const resourceTitle = computed(() => pickTranslation(props.resource?.title, state.locale));
const contentContainerTitle = computed(() =>
  !props.resource.contents?.length ? $t('browse.locationResourceNoData') : undefined
);

const contentContainerRef = ref();
const isContentContainerHovered = useElementHover(contentContainerRef, {
  delayEnter: 0,
  delayLeave: 0,
});
const headerWidgetsOpacity = computed<number>(() =>
  isContentContainerHovered.value || state.isTouchDevice ? 1 : browse.focusView ? 0 : 0.2
);

const collapsable = computed(
  () =>
    !browse.focusView && contentsLoaded.value && !!props.resource.config.general.defaultCollapsed
);
const collapsed = ref(!!props.resource.config.general.defaultCollapsed);
watch(
  () => browse.focusView,
  (focusView) => {
    collapsed.value = !focusView && !!props.resource.config.general.defaultCollapsed;
  },
  { immediate: true }
);
</script>

<template>
  <div
    v-if="resource.active && (contentsLoaded || !browse.focusView)"
    ref="contentContainerRef"
    class="content-block content-container"
    :class="{ empty: !contentsLoaded }"
    :title="contentContainerTitle"
  >
    <n-flex
      align="center"
      :wrap="false"
      :size="[12, 0]"
      class="content-header mb-sm"
      :class="{ 'mb-0': browse.focusView || !contentsLoaded }"
    >
      <n-flex align="center" :gap="12" :class="{ translucent: !contentsLoaded }" style="flex: 2">
        <div
          class="text-color-accent"
          :class="{ 'text-small': browse.focusView, b: browse.focusView }"
        >
          {{ resourceTitle }}
        </div>
        <n-flex v-if="!browse.focusView" align="center" :wrap="false">
          <!-- icon hint: publication status -->
          <n-icon
            v-if="!resource.public && !resource.proposed"
            :component="PublicOffIcon"
            :color="themeVars.errorColor"
            :title="$t('resources.notPublic')"
            size="medium"
          />
          <n-icon
            v-else-if="resource.proposed"
            :component="ProposedIcon"
            :color="themeVars.warningColor"
            :title="$t('resources.proposed')"
            size="medium"
          />
          <!-- icon hint: this is combined content (context) from original level -->
          <n-icon
            v-if="contentContextLoaded"
            :component="MergeIcon"
            size="medium"
            :title="
              $t('browse.contents.isContentContext', {
                level: state.textLevelLabels[props.resource.level],
              })
            "
          />
          <!-- icon hint: no content -->
          <n-icon
            v-else-if="
              !contentsLoaded &&
              (resource.level === browse.level ||
                (onChildLevel && resource.config.common.enableContentContext))
            "
            :component="NoContentIcon"
            size="medium"
          />
          <!-- icon hint: cannot display possible content from original level -->
          <n-icon
            v-else-if="!contentsLoaded"
            :component="WarningIcon"
            size="medium"
            :title="$t('browse.contents.cannotShowContext')"
          />
          <n-tag
            v-if="!browse.focusView && props.resource.level !== browse.level"
            size="small"
            :title="`${$t('models.text.level')}: ${state.textLevelLabels[props.resource.level]}`"
          >
            <template #icon>
              <n-icon :component="LevelsIcon" />
            </template>
            {{ state.textLevelLabels[props.resource.level] }}
          </n-tag>
        </n-flex>
        <n-flex
          v-if="loading && !contentsLoaded && !browse.focusView"
          align="center"
          size="small"
          :wrap="false"
          class="mx-lg text-small translucent"
          style="flex: 2"
        >
          <n-icon :component="HourglassIcon" />
          <span>{{ $t('general.loading') }}</span>
        </n-flex>
      </n-flex>
      <content-header-widget-bar
        :resource="resource"
        :opacity="headerWidgetsOpacity"
        :small-screen="state.smallScreen"
      />
    </n-flex>

    <n-spin :show="loading && contentsLoaded" size="small" :delay="200">
      <collapsable-content
        v-if="contentsLoaded"
        :collapsable="collapsable || contentContextLoaded"
        :collapsed="collapsed"
        :height-tresh-px="320"
      >
        <!-- content-specific component (that displays the actual content) -->
        <component
          :is="contentComponents[resource.resourceType]"
          :resource="resource"
          :focus-view="browse.focusView"
          :dir="resource.config.common.rtl ? 'rtl' : undefined"
        />
      </collapsable-content>
    </n-spin>
  </div>
</template>

<style scoped>
.content-container {
  padding-top: var(--gap-md);
  padding-bottom: var(--gap-md);
  font-size: var(--font-size);
}

.focus-view .content-container {
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
  margin: 0;
  box-shadow: none;
  border-radius: 0;
}

.focus-view .content-container:first-child {
  border-top-left-radius: var(--border-radius);
  border-top-right-radius: var(--border-radius);
  margin-top: var(--gap-lg);
}

.focus-view .content-container:last-child {
  border-bottom-left-radius: var(--border-radius);
  border-bottom-right-radius: var(--border-radius);
  margin-bottom: var(--gap-lg);
}

.focus-view .content-container:not(:first-child) {
  border-top: 1px solid var(--main-bg-color);
  margin-bottom: 0;
}

.content-container.empty {
  background-color: var(--main-bg-color);
  border: 2px dashed var(--main-bg-color);
  box-shadow: none;
  padding: 12px var(--gap-lg);
}
</style>
