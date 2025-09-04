<script setup lang="ts">
import type { AnyResourceRead } from '@/api';
import ContentHeaderWidgetBar from '@/components/browse/ContentHeaderWidgetBar.vue';
import CollapsibleContent from '@/components/CollapsibleContent.vue';
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
import { NFlex, NIcon, NSpin, NTag } from 'naive-ui';
import { computed, ref, watch } from 'vue';

const props = defineProps<{
  loading?: boolean;
  resource: AnyResourceRead;
}>();

const browse = useBrowseStore();
const state = useStateStore();

const showComments = ref(props.resource.config.general.showComments);
const hasContents = computed(() => !!props.resource.contents?.length);
const onChildLevel = computed(() => props.resource.level - 1 === browse.level);
const contentContextLoaded = computed(() => hasContents.value && onChildLevel.value);

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

const collapsible = computed(
  () =>
    !browse.focusView && hasContents.value && !!props.resource.config.general.collapsibleContents
);
const collapsed = ref(!!props.resource.config.general.collapsibleContents);
watch(
  () => browse.focusView,
  (focusView) => {
    collapsed.value = !focusView && !!props.resource.config.general.collapsibleContents;
  },
  { immediate: true }
);
</script>

<template>
  <div
    v-if="resource.active && (hasContents || !browse.focusView)"
    ref="contentContainerRef"
    class="content-block"
    :class="{ empty: !hasContents }"
    :title="contentContainerTitle"
  >
    <n-flex
      align="center"
      :wrap="false"
      :size="[12, 0]"
      class="content-header mb-sm"
      :class="{ 'mb-0': browse.focusView || !hasContents }"
    >
      <n-flex align="center" :gap="12" :class="{ translucent: !hasContents }" style="flex: 2">
        <div
          :class="{
            'text-medium': !browse.focusView,
            'text-small': browse.focusView,
            translucent: true,
          }"
        >
          {{ resourceTitle }}
        </div>
        <n-flex v-if="!browse.focusView" align="center" :wrap="false">
          <!-- icon hint: publication status -->
          <n-icon
            v-if="!resource.public && !resource.proposed"
            :component="PublicOffIcon"
            color="var(--error-color)"
            :title="$t('resources.notPublic')"
            size="medium"
          />
          <n-icon
            v-else-if="resource.proposed"
            :component="ProposedIcon"
            color="var(--warning-color)"
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
              !loading &&
              !hasContents &&
              (resource.level === browse.level ||
                (onChildLevel && resource.config.general.enableContentContext))
            "
            :component="NoContentIcon"
            size="medium"
          />
          <!-- icon hint: cannot display possible content from original level -->
          <n-icon
            v-else-if="!loading && !hasContents"
            :component="WarningIcon"
            size="medium"
            :title="$t('browse.contents.cannotShowContext')"
          />
          <n-tag
            v-if="!browse.focusView && props.resource.level !== browse.level"
            size="small"
            :title="`${$t('common.level')}: ${state.textLevelLabels[props.resource.level]}`"
          >
            <template #icon>
              <n-icon :component="LevelsIcon" />
            </template>
            {{ state.textLevelLabels[props.resource.level] }}
          </n-tag>
        </n-flex>
        <n-flex
          v-if="loading && !hasContents && !browse.focusView"
          align="center"
          size="small"
          :wrap="false"
          class="mx-lg text-small translucent"
          style="flex: 2"
        >
          <n-icon :component="HourglassIcon" />
          <span>{{ $t('common.loading') }}</span>
        </n-flex>
      </n-flex>
      <content-header-widget-bar
        v-model:show-comments="showComments"
        :resource="resource"
        :opacity="headerWidgetsOpacity"
        :small-screen="state.smallScreen"
      />
    </n-flex>

    <n-spin :show="loading && hasContents" size="small" :delay="1500">
      <collapsible-content
        v-if="hasContents"
        :collapsible="collapsible || contentContextLoaded"
        :collapsed="collapsed"
        :height-tresh-px="resource.config.general.collapsibleContents || undefined"
        class="content-loadable"
        :class="{ 'content-loading': loading }"
      >
        <!-- content-specific component (that displays the actual content) -->
        <component
          :is="contentComponents[resource.resourceType]"
          :resource="resource"
          :focus-view="browse.focusView"
          :show-comments="showComments && !browse.focusView"
          :dir="resource.config.general.rtl ? 'rtl' : undefined"
        />
      </collapsible-content>
    </n-spin>
  </div>
</template>

<style scoped>
.content-block {
  padding-right: var(--gap-md);
}

.focus-view .content-block {
  padding-right: var(--gap-sm);
  margin: 0;
  box-shadow: none;
  border-radius: 0;
}

.focus-view .content-block:first-child {
  border-top-left-radius: var(--border-radius);
  border-top-right-radius: var(--border-radius);
  margin-top: var(--gap-lg);
}

.focus-view .content-block:last-child {
  border-bottom-left-radius: var(--border-radius);
  border-bottom-right-radius: var(--border-radius);
  margin-bottom: var(--gap-lg);
}

.focus-view .content-block:not(:first-child) {
  border-top: 1px solid var(--main-bg-color);
  margin-bottom: 0;
}

.content-block.empty {
  background-color: var(--main-bg-color);
  border: 2px dashed var(--main-bg-color);
  box-shadow: none;
  padding: 12px var(--gap-lg);
}

:deep(.n-spin-content.n-spin-content--spinning) {
  opacity: 1;
  pointer-events: inherit;
  cursor: wait;
}
</style>
