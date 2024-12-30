<script setup lang="ts">
import type { SearchHit, TextRead } from '@/api';
import CollapsableContent from '@/components/CollapsableContent.vue';
import { BookIcon, LevelsIcon, StarHalfIcon, TextsIcon } from '@/icons';
import { transparentize } from 'color2k';
import { NFlex, NIcon, NListItem, NTag } from 'naive-ui';
import { computed } from 'vue';

const props = defineProps<{
  id: SearchHit['id'];
  label: SearchHit['label'];
  fullLabel: SearchHit['fullLabel'];
  fullLabelAsTitle?: boolean;
  textTitle: TextRead['title'];
  textSlug: TextRead['slug'];
  textColor: TextRead['accentColor'];
  level: SearchHit['level'];
  levelLabel: string;
  position: SearchHit['position'];
  scorePercent?: number;
  highlight?: SearchHit['highlight'];
  smallScreen?: boolean;
  resourceTitles: { [id: string]: string };
}>();
export type SearchResultProps = typeof props;

const emit = defineEmits(['navigate']);

const textTagColor = computed(() => transparentize(props.textColor, 0.8));
const resultHoverColor = computed(() => transparentize(props.textColor, 0.9));
const scorePercentDisplay = computed(() =>
  props.scorePercent ? props.scorePercent.toFixed(1) + '%' : '–'
);
const scoreTagColor = computed(() =>
  props.scorePercent
    ? `rgba(${180 - props.scorePercent * 1.8}, ${props.scorePercent * 1.8}, 0, 0.25)`
    : undefined
);
const highlightsProcessed = computed<Record<string, string>>(() => {
  if (!props.highlight) return {};
  return Object.fromEntries(
    Object.entries(props.highlight).map(([k, v]) => [props.resourceTitles[k], v.join(' ... ')])
  );
});
</script>

<template>
  <n-list-item style="padding: 0">
    <collapsable-content
      :collapsable="props.smallScreen"
      :collapsed="smallScreen"
      :scrollable="false"
      :height-tresh-px="250"
      :show-btn-text="!smallScreen"
      class="mb-sm"
    >
      <n-flex
        vertical
        size="small"
        class="sr-container"
        :style="{ borderTopColor: textColor }"
        @click="emit('navigate')"
      >
        <n-flex wrap align="center" :title="fullLabel">
          <div class="sr-header-title" :style="{ color: textColor }">
            {{ fullLabelAsTitle ? fullLabel : label }}
          </div>
          <div class="sr-header-tags">
            <n-tag size="small" :bordered="false" :color="{ color: textTagColor }">
              <template #icon>
                <n-icon class="translucent" :component="TextsIcon" />
              </template>
              {{ textTitle }}
            </n-tag>
            <n-tag size="small" :bordered="false">
              <template #icon>
                <n-icon class="translucent" :component="LevelsIcon" />
              </template>
              {{ levelLabel }}
            </n-tag>
            <n-tag size="small" :bordered="false" :color="{ color: scoreTagColor }">
              <template #icon>
                <n-icon class="translucent" :component="StarHalfIcon" />
              </template>
              {{ scorePercentDisplay }}
            </n-tag>
          </div>
        </n-flex>
        <div
          v-if="!fullLabelAsTitle"
          class="sr-location text-tiny translucent ellipsis"
          :title="fullLabel"
        >
          <n-icon :component="BookIcon" />
          {{ fullLabel }}
        </div>
        <div class="sr-highlights">
          <div v-for="(hl, key) in highlightsProcessed" :key="key" :title="key">
            <span class="b" :style="{ color: textColor }">{{ key }}: </span>
            <span class="content-font" v-html="hl"></span>
          </div>
        </div>
      </n-flex>
    </collapsable-content>
  </n-list-item>
</template>

<style scoped>
.sr-container {
  padding: var(--gap-sm) var(--gap-md);
  cursor: pointer;
  border-radius: var(--border-radius);
  border-top-style: solid;
  border-top-width: 1px;
  transition: background-color 0.2s ease;
}

.sr-container:hover {
  background-color: v-bind(resultHoverColor);
}

.sr-header-title {
  font-weight: var(--font-weight-bold);
  flex-grow: 2;
}

.sr-header-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.sr-location {
  display: flex;
  align-items: center;
  flex-wrap: nowrap;
  column-gap: 0.5rem;
}

.sr-highlights {
  display: flex;
  flex-direction: column;
  font-size: var(--font-size-medium);
  gap: 0.3rem;
}
</style>

<style>
.sr-highlights em {
  font-style: normal;
  padding: 0 2px;
  background-color: #9994;
  border-radius: 2px;
}
</style>
