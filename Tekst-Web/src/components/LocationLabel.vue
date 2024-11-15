<script setup lang="ts">
import type { LocationRead } from '@/api';
import { useBrowseStore, useStateStore } from '@/stores';
import { getFullLocationLabel } from '@/utils';
import { computed } from 'vue';

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
  getFullLocationLabel(
    locationPath.value.filter((n) => n.level <= (props.maxLevel ?? Number.MAX_SAFE_INTEGER)),
    state.textLevelLabels,
    state.text
  )
);
</script>

<template>
  {{ locationLabel }}
</template>
