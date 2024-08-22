<script setup lang="ts">
import type { SearchHit, TextRead } from '@/api';
import { BookIcon } from '@/icons';
import Color from 'color';
import { NListItem, NTag, NIcon } from 'naive-ui';
import { computed } from 'vue';
import { RouterLink } from 'vue-router';

const props = defineProps<{
  id: SearchHit['id'];
  label: SearchHit['label'];
  fullLabel: SearchHit['fullLabel'];
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

const textTagColor = computed(() => Color(props.textColor).fade(0.6).rgb().string());
const scorePercentDisplay = computed(() =>
  props.scorePercent ? props.scorePercent.toFixed(1) + '%' : '–'
);
const scoreTagColor = computed(() =>
  props.scorePercent
    ? `rgba(${180 - props.scorePercent * 1.8}, ${props.scorePercent * 1.8}, 0, 0.25)`
    : undefined
);
const linkTargetRoute = computed(() => ({
  name: 'browse',
  params: { text: props.textSlug },
  query: { lvl: props.level, pos: props.position },
}));
const highlightsProcessed = computed<Record<string, string>>(() => {
  if (!props.highlight) return {};
  return Object.fromEntries(
    Object.entries(props.highlight).map(([k, v]) => [props.resourceTitles[k], v.join(' ... ')])
  );
});
</script>

<template>
  <n-list-item style="padding: 0">
    <router-link :to="linkTargetRoute" class="sr-link">
      <div class="sr-container">
        <div class="sr-header" :title="fullLabel">
          <div class="sr-header-title" :style="{ color: textColor }">
            {{ label }}
          </div>
          <div class="sr-header-tags">
            <n-tag size="small" :bordered="false" :color="{ color: textTagColor }">
              {{ textTitle }}
            </n-tag>
            <n-tag size="small" :bordered="false">
              {{ levelLabel }}
            </n-tag>
            <n-tag size="small" :bordered="false" :color="{ color: scoreTagColor }">
              {{ $t('search.results.relevance') }}: {{ scorePercentDisplay }}
            </n-tag>
          </div>
        </div>
        <div class="sr-location text-small translucent ellipsis" :title="fullLabel">
          <n-icon :component="BookIcon" />
          {{ fullLabel }}
        </div>
        <div class="sr-highlights">
          <div v-for="(hl, key) in highlightsProcessed" :key="key" :title="key">
            <span class="b" :style="{ color: textColor }">{{ key }}: </span>
            <!-- eslint-disable-next-line vue/no-v-html -->
            <span class="content-font" v-html="hl"></span>
          </div>
        </div>
      </div>
    </router-link>
  </n-list-item>
</template>

<style scoped>
.sr-container {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  padding: var(--gap-md);
}
.sr-link {
  color: inherit;
  text-decoration: inherit;
  font-style: inherit;
  font-weight: inherit;
}
.sr-header {
  display: flex;
  align-items: center;
  column-gap: var(--gap-md);
  row-gap: 0.25rem;
  flex-wrap: wrap;
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
