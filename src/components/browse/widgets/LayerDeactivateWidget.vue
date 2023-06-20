<script setup lang="ts">
import ClearRound from '@vicons/material/ClearRound';
import UnitContainerHeaderWidget from '@/components/browse/UnitContainerHeaderWidget.vue';
import { useBrowseStore } from '@/stores';

const props = defineProps<{
  layerId: string;
}>();

const browse = useBrowseStore();

function handleClick() {
  const layer = browse.layers.find((l) => l.id == props.layerId);
  layer && (layer.active = false);
}
</script>

<template>
  <UnitContainerHeaderWidget
    :title="$t('browse.deactivateWidget.title')"
    :iconComponent="ClearRound"
    @click="handleClick"
  />
</template>
