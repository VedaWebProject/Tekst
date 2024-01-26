<script setup lang="ts">
import { computed } from 'vue';
import { useStateStore, useBrowseStore } from '@/stores';
import type { LocationRead } from '@/api';

const props = defineProps<{
  locationPath?: LocationRead[];
  locationLabels?: string[];
  maxLevel?: number;
}>();

const state = useStateStore();
const browse = useBrowseStore();
const locationPath = computed<LocationRead[]>(
  () =>
    props.locationPath ??
    props.locationLabels?.map((ll, i) => ({
      level: i,
      id: '',
      label: ll,
      position: 0,
      textId: state.text?.id || '',
    })) ??
    browse.locationPath ??
    []
);

const locationLabel = computed(() =>
  locationPath.value
    .filter((n) => n.level <= (props.maxLevel ?? Number.MAX_SAFE_INTEGER))
    .map((n) => {
      if (!n.label) return '';
      const lvlLabel = state.textLevelLabels[n.level];
      const locationPrefix = state.text?.labeledLocation && lvlLabel ? `${lvlLabel}: ` : '';
      return locationPrefix + n.label;
    })
    .join(state.text?.locDelim || ', ')
);
</script>

<template>
  {{ locationLabel }}
</template>
