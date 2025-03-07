<script setup lang="ts">
import type { SearchHit, TextRead } from '@/api';
import CollapsableContent from '@/components/CollapsableContent.vue';
import { $t } from '@/i18n';
import { BookIcon, LevelsIcon, StarHalfIcon, TextsIcon } from '@/icons';
import { useResourcesStore, useStateStore } from '@/stores';
import { transparentize } from 'color2k';
import { NFlex, NIcon, NListItem, NTag } from 'naive-ui';
import { computed } from 'vue';

type HighlightDisplayData = {
  id: string;
  level: number;
  title: string;
  hl: string;
  tip?: string;
};

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
}>();
export type SearchResultProps = typeof props;

const emit = defineEmits(['navigate']);

const state = useStateStore();
const resources = useResourcesStore();

const textColorTranslucent = computed(() => transparentize(props.textColor, 0.6));
const resultHoverColor = computed(() => transparentize(props.textColor, 0.9));

const scorePercentDisplay = computed(() =>
  props.scorePercent ? props.scorePercent.toFixed(1) + '%' : '–'
);

const scoreTagColor = computed(() => {
  if (!props.scorePercent) return;
  const red = 140 - (props.scorePercent / 100) * 140;
  const green = (props.scorePercent / 100) * 140;
  return `rgba(${red}, ${green}, 0, 1)`;
});

const highlightsProcessed = computed<HighlightDisplayData[]>(() => {
  if (!props.highlight) return [];
  return Object.entries(props.highlight)
    .map(([id, hl]) => {
      const level = resources.all.find((r) => r.id === id)?.level || 0;
      const title = resources.resourceTitles[id];
      return {
        id,
        level,
        title,
        hl: hl.join(' ... '),
        tip:
          level < props.level
            ? $t('search.results.higherLvlHit', { level: state.textLevelLabels[level] })
            : undefined,
      };
    })
    .sort((a, b) => b.level - a.level);
});
</script>

<template>
  <n-list-item style="padding: 0">
    <collapsable-content
      :height-tresh-px="smallScreen ? 250 : 420"
      :show-btn-text="!smallScreen"
      class="mb-sm"
    >
      <n-flex vertical size="small" class="sr-container" @click="emit('navigate')">
        <n-flex wrap align="center" :title="fullLabel">
          <n-flex align="center" :wrap="false" style="flex: 2">
            <n-icon :component="BookIcon" class="text-medium" />
            <b>{{ fullLabelAsTitle ? fullLabel : label }}</b>
          </n-flex>
          <div class="sr-header-tags">
            <n-tag
              size="small"
              :color="{ borderColor: textColorTranslucent, textColor: textColor }"
            >
              <template #icon>
                <n-icon class="translucent" :component="TextsIcon" />
              </template>
              {{ textTitle }}
            </n-tag>
            <n-tag size="small">
              <template #icon>
                <n-icon class="translucent" :component="LevelsIcon" />
              </template>
              {{ levelLabel }}
            </n-tag>
            <n-tag size="small" :color="{ textColor: scoreTagColor }">
              <template #icon>
                <n-icon class="translucent" :component="StarHalfIcon" />
              </template>
              {{ scorePercentDisplay }}
            </n-tag>
          </div>
        </n-flex>
        <div v-if="!fullLabelAsTitle" class="text-tiny translucent ellipsis" :title="fullLabel">
          {{ fullLabel }}
        </div>
        <div class="sr-highlights">
          <div
            v-for="hl in highlightsProcessed"
            :key="hl.id"
            :title="hl.tip"
            :class="{ translucent: hl.level < level }"
          >
            <span class="b" :style="{ color: textColor }">{{ hl.title }}: </span>
            <span class="content-font" v-html="hl.hl"></span>
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
  border-top: v-bind('`2px solid ${textColorTranslucent}`');
  transition: background-color 0.2s ease;
}

.sr-container:hover {
  background-color: v-bind(resultHoverColor);
}

.sr-header-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
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
