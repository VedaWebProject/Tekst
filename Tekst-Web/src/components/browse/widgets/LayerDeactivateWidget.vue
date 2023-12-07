<script setup lang="ts">
import ClearRound from '@vicons/material/ClearRound';
import UnitContainerHeaderWidget from '@/components/browse/UnitContainerHeaderWidget.vue';
import { useBrowseStore } from '@/stores';
import { useMessages } from '@/messages';
import { $t } from '@/i18n';
import type { AnyLayerRead } from '@/api';

const props = defineProps<{
  layer: AnyLayerRead;
}>();

const browse = useBrowseStore();
const { message } = useMessages();

function handleClick() {
  browse.deactivateLayer(props.layer.id);
  message.info(
    $t('browse.units.widgets.deactivateWidget.message', { layerTitle: props.layer.title })
  );
}
</script>

<template>
  <UnitContainerHeaderWidget
    :title="$t('browse.units.widgets.deactivateWidget.title')"
    :icon-component="ClearRound"
    @click="handleClick"
  />
</template>
