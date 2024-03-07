<script setup lang="ts">
import type { SearchHit } from '@/api';
import Color from 'color';
import { NListItem, NTag } from 'naive-ui';
import { computed } from 'vue';

export interface SearchResultProps {
  id: SearchHit['id'];
  label: SearchHit['label'];
  fullLabel: SearchHit['fullLabel'];
  text: string;
  textColor: string;
  level: SearchHit['level'];
  levelLabel: string;
  position: SearchHit['position'];
  scorePercent: number;
  smallScreen?: boolean;
}

const props = defineProps<SearchResultProps>();
const emit = defineEmits(['click']);
const textTagColor = computed(() => Color(props.textColor).fade(0.75).rgb().string());
const scoreTagColor = computed(
  () => `rgba(${180 - props.scorePercent * 1.8}, ${props.scorePercent * 1.8}, 0, 0.2)`
);
</script>

<template>
  <n-list-item class="sr-item" :title="fullLabel" @click="emit('click', props)">
    <div class="sr-container">
      <div class="sr-header ellipsis">
        {{ fullLabel }} bar foo bar foo bar foo bar foo bar foo bar foo bar foo bar foo bar foo bar
        foo bar foo bar foo bar foo bar foo bar foo bar foo bar foo bar foo bar foo bar foo bar foo
        bar foo bar foo bar foo bar foo bar foo bar foo bar
      </div>
      <div class="sr-body">
        <div class="ellipsis">
          foo foo foo foo foo foo foo foo foo foo foo foo foo foo foo foo foo foo foo foo foo foo
          foo foo foo foo foo foo foo foo foo foo foo foo foo foo foo foo
        </div>
        <div class="ellipsis">
          bar bar bar bar bar bar bar bar bar bar bar bar bar bar bar bar bar bar bar bar bar bar
          bar bar bar bar bar bar bar bar bar bar bar bar bar bar bar bar
        </div>
      </div>
      <div class="sr-footer">
        <n-tag size="small" :bordered="false" :color="{ color: textTagColor }">
          {{ text }}
        </n-tag>
        <n-tag size="small" :bordered="false">
          {{ levelLabel }}
        </n-tag>
        <n-tag size="small" :bordered="false" :color="{ color: scoreTagColor }">
          Relevance: {{ scorePercent }}%
        </n-tag>
      </div>
    </div>
  </n-list-item>
</template>

<style scoped>
.sr-container {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}
.sr-header {
  font-weight: var(--font-weight-bold);
}
.sr-body {
  display: flex;
  flex-direction: column;
}
.sr-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--content-gap);
}
.ellipsis {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
