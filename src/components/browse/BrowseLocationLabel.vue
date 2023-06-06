<script setup lang="ts">
import { computed } from 'vue';
import { useStateStore, useBrowseStore } from '@/stores';

const state = useStateStore();
const browse = useBrowseStore();

const browseLocationLabel = computed(() =>
  browse.nodePath
    .map((n) => {
      const lvlLabel = state.textLevelLabels[n.level];
      const nodePrefix = state.text?.labeledLocation && lvlLabel ? `${lvlLabel}: ` : '';
      return n.label ? `${nodePrefix}${n.label}` : '';
    })
    .join(state.text?.locDelim || ', ')
);
</script>

<template>
  <span>{{ browseLocationLabel }}</span>
</template>
