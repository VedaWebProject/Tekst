<script setup lang="ts">
import { computed } from 'vue';
import { useStateStore, useBrowseStore } from '@/stores';
import type { LocationRead } from '@/api';

const props = defineProps<{
  locationPath?: LocationRead[];
  maxLevel?: number;
}>();

const state = useStateStore();
const browse = useBrowseStore();

const locationLabel = computed(() =>
  (props.locationPath || browse.locationPath)
    .filter((n) => n.level <= (props.maxLevel ?? Number.MAX_SAFE_INTEGER))
    .map((n) => {
      const lvlLabel = state.textLevelLabels[n.level];
      const locationPrefix = state.text?.labeledLocation && lvlLabel ? `${lvlLabel}: ` : '';
      return n.label ? `${locationPrefix}${n.label}` : '';
    })
    .join(state.text?.locDelim || ', ')
);
</script>

<template>
  {{ locationLabel }}
</template>
