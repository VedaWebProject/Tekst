<script setup lang="ts">
import { computed } from 'vue';
import { useStateStore, useBrowseStore } from '@/stores';
import type { NodeRead } from '@/api';

const props = defineProps<{
  nodePath?: NodeRead[];
  maxLevel?: number;
}>();

const state = useStateStore();
const browse = useBrowseStore();

const locationLabel = computed(() =>
  (props.nodePath || browse.nodePath)
    .filter((n) => n.level <= (props.maxLevel ?? Number.MAX_SAFE_INTEGER))
    .map((n) => {
      const lvlLabel = state.textLevelLabels[n.level];
      const nodePrefix = state.text?.labeledLocation && lvlLabel ? `${lvlLabel}: ` : '';
      return n.label ? `${nodePrefix}${n.label}` : '';
    })
    .join(state.text?.locDelim || ', ')
);
</script>

<template>
  {{ locationLabel }}
</template>
