<script setup lang="ts">
import type { SearchHit } from '@/api';
import { NListItem, NThing } from 'naive-ui';

export interface SearchResultProps {
  id: SearchHit['id'];
  label: SearchHit['label'];
  text: string;
  textColor: string;
  level: SearchHit['level'];
  levelLabel: string;
  position: SearchHit['position'];
  score: SearchHit['score'];
}

const props = defineProps<SearchResultProps>();
const emit = defineEmits(['click']);
</script>

<template>
  <n-list-item @click="emit('click', props)">
    <n-thing>
      <template #header> {{ levelLabel }}: {{ label }} </template>
    </n-thing>
  </n-list-item>
</template>
