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
const textTagColor = computed(() => Color(props.textColor).fade(0.6).rgb().string());
const scorePercentDisplay = computed(() => props.scorePercent.toFixed(1) + '%');
const scoreTagColor = computed(
  () => `rgba(${180 - props.scorePercent * 1.8}, ${props.scorePercent * 1.8}, 0, 0.3)`
);
</script>

<template>
  <n-list-item class="sr-item" @click="emit('click', props)">
    <div class="sr-container">
      <div class="sr-header" :title="fullLabel">{{ levelLabel }}: {{ label }}</div>
      <div v-if="label !== fullLabel" class="text-small i translucent">
        {{ fullLabel }}
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
      <div class="sr-tags">
        <n-tag size="small" :bordered="false" :color="{ color: textTagColor }">
          {{ text }}
        </n-tag>
        <n-tag size="small" :bordered="false">
          {{ levelLabel }}
        </n-tag>
        <n-tag size="small" :bordered="false" :color="{ color: scoreTagColor }">
          Relevance: {{ scorePercentDisplay }}
        </n-tag>
      </div>
    </div>
  </n-list-item>
</template>

<style scoped>
.sr-container {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}
.sr-header {
  font-weight: var(--font-weight-bold);
}
.sr-body {
  display: flex;
  flex-direction: column;
}
.sr-tags {
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
