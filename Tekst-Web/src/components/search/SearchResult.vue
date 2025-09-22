<script setup lang="ts">
import type { SearchHit, TextRead } from '@/api';
import CollapsibleContent from '@/components/CollapsibleContent.vue';
import { $t } from '@/i18n';
import { BookIcon, LevelsIcon, StarHalfIcon, TextsIcon } from '@/icons';
import { useResourcesStore, useStateStore, useThemeStore } from '@/stores';
import { lighten, toRgba, transparentize } from 'color2k';
import { NFlex, NIcon, NListItem, NTag } from 'naive-ui';
import { computed } from 'vue';

type HighlightDisplayData = {
  id: string;
  level: number;
  title: string;
  hl: string;
  tip?: string;
  font?: string;
};

const props = defineProps<{
  id: SearchHit['id'];
  label: SearchHit['label'];
  fullLabel: SearchHit['fullLabel'];
  fullLabelAsTitle?: boolean;
  textTitle: TextRead['title'];
  textSlug: TextRead['slug'];
  textColor: TextRead['color'];
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
const theme = useThemeStore();

const textColorTranslucent = computed(() => toRgba(transparentize(props.textColor, 0.6)));
const resultHoverColor = computed(() => toRgba(transparentize(props.textColor, 0.9)));

const scorePercentDisplay = computed(() =>
  props.scorePercent ? props.scorePercent.toFixed(1) + '%' : '–'
);

const scoreTagColor = computed(() => {
  if (!props.scorePercent) return;
  const red = Math.round(140 - (props.scorePercent / 100) * 140);
  const green = Math.round((props.scorePercent / 100) * 140);
  return lighten(`rgba(${red}, ${green}, 0, 1)`, theme.dark ? 0.5 : 0);
});

const scoreTagBorderColor = computed(() =>
  scoreTagColor.value ? transparentize(scoreTagColor.value, 0.75) : undefined
);

const highlightsProcessed = computed<HighlightDisplayData[]>(() => {
  if (!props.highlight) return [];
  return Object.entries(props.highlight)
    .map(([id, hl]) => {
      const res = resources.all.find((r) => r.id === id);
      if (!res) return;
      const level = res.level || 0;
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
        font: res.contentFont,
      };
    })
    .filter((hl) => !!hl)
    .sort((a, b) => b.level - a.level);
});
</script>

<template>
  <n-list-item style="padding: 0">
    <collapsible-content
      :height-tresh-px="smallScreen ? 250 : 420"
      :show-btn-text="!smallScreen"
      class="mb-sm"
    >
      <n-flex vertical size="small" class="sr-container" @click="emit('navigate')">
        <n-flex wrap align="center">
          <n-flex align="center" :wrap="false" style="flex: 2">
            <n-icon :component="BookIcon" class="text-medium" />
            <b class="text-medium">{{ fullLabelAsTitle ? fullLabel : label }}</b>
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
            <n-tag
              size="small"
              :color="{ textColor: scoreTagColor, borderColor: scoreTagBorderColor }"
            >
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
            <span>{{ hl.title }}: </span>
            <span :style="{ fontFamily: hl.font }" v-html="hl.hl"></span>
          </div>
        </div>
      </n-flex>
    </collapsible-content>
  </n-list-item>
</template>

<style scoped>
.sr-container {
  padding: var(--gap-sm) var(--gap-md);
  cursor: pointer;
  border-radius: var(--border-radius);
  border-left: v-bind('`6px solid ${textColor}`');
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
