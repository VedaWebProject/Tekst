<script setup lang="ts">
import UnitContainerHeaderWidget from '@/components/browse/UnitContainerHeaderWidget.vue';
import { useMessages } from '@/messages';
import MergeRound from '@vicons/material/MergeRound';

// const props = defineProps<{
//   layer: Record<string, any>;
// }>();

const { message } = useMessages();

function handleClick() {
  message.warning('NOT IMPLEMENTED!');
  // TODO
}
</script>

<template>
  <UnitContainerHeaderWidget
    :title="$t('browse.units.widgets.mergeWidget.title')"
    :iconComponent="MergeRound"
    @click="handleClick"
  />
</template>
